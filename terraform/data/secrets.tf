# ------------------------------------------------------------
# Secrets Manager (DB接続情報)
#
# 設計判断:
# - マスター認証情報(username/password)はfoundation層が所有する。
#   この層はそれを「読む」だけ。パスワードの寿命 = foundationの寿命なので、
#   dataをdestroy→スナップショット復元しても、DBのパスワード
#   (スナップショット取得時点の値)とシークレットが常に一致する
# - この層が作るのは「接続用シークレット」(host込みのdatabase_url)。
#   hostはRDSを作り直すたびに変わるため、RDSと運命を共にするこの層が持つ。
#   destroyで消えても、再applyすれば「不変のパスワード + 新しいhost」で
#   同じ内容を再生成できる
# - recovery_window_in_days = 0 で即時削除にし、destroy→再apply時の
#   同名シークレット衝突を防ぐ(マスター認証情報はfoundation側に残るため、
#   ここに復旧猶予が必要な情報はない)
#
# - ECSタスク実行ロールへのGetSecretValue許可はこの層で付与する。
#   接続用シークレットのARNはここで初めて確定するため
# ------------------------------------------------------------

# --- foundation層のマスター認証情報を読む ---
data "aws_ssm_parameter" "db_master_secret_arn" {
  name = "${local.ssm_prefix}/db_master_secret_arn"
}

data "aws_secretsmanager_secret_version" "db_master" {
  secret_id = data.aws_ssm_parameter.db_master_secret_arn.value
}

locals {
  # rds.tf の username/password はここを参照する
  db_creds = jsondecode(data.aws_secretsmanager_secret_version.db_master.secret_string)
}

# --- 接続用シークレット(app層がECSタスクに注入する) ---
resource "aws_secretsmanager_secret" "db" {
  name                    = "${var.project}/db-connection"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "db" {
  secret_id = aws_secretsmanager_secret.db.id

  secret_string = jsonencode({
    username = local.db_creds.username
    password = local.db_creds.password
    host     = aws_db_instance.main.address
    port     = 5432
    dbname   = var.db_name
    # アプリがそのまま使える接続文字列も同梱
    database_url = "postgresql+psycopg://${local.db_creds.username}:${local.db_creds.password}@${aws_db_instance.main.address}:5432/${var.db_name}"
  })
}

# --- ECSタスク実行ロールにシークレット読み取りを許可 ---
# ロール本体はfoundation層、ポリシーはARNが確定するこの層で付与
resource "aws_iam_role_policy" "task_execution_secrets" {
  name = "${var.project}-read-db-secret"
  role = split("/", data.aws_ssm_parameter.task_execution_role_arn.value)[1] # ARN→ロール名

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["secretsmanager:GetSecretValue"]
        Resource = [aws_secretsmanager_secret.db.arn]
      }
    ]
  })
}
