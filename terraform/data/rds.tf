# ------------------------------------------------------------
# RDS PostgreSQL
#
# 設計判断:
# - snapshot_identifier変数で「新規作成」と「スナップショット復元」を
#   1つのコードで切り替える
# - destroy時は必ず最終スナップショットを自動作成(skip_final_snapshot=false)
#   → 「消してもデータは戻せる」を構造で保証する
# - foundation層のシークレットを参照
#
# ハマりどころ(重要):
# - スナップショット復元時、DBのマスターパスワードは「スナップショット
#   取得時点の値」になる。Terraformのpassword引数は復元時には無視される。
#   → 本構成ではパスワードをSecrets Managerに永続化し、DBを作り直しても
#     同じシークレットを使い続けることで、この問題を回避している
#     (シークレットはdestroyしても残す設計。secrets.tf参照)
# ------------------------------------------------------------

resource "aws_db_subnet_group" "main" {
  name       = "${var.project}-db-subnet-group"
  subnet_ids = local.private_subnet_ids
}

resource "aws_db_instance" "main" {
  identifier = "${var.project}-db"

  # --- エンジン ---
  engine         = "postgres"
  engine_version = "16"
  instance_class = var.db_instance_class

  # --- ストレージ ---
  allocated_storage = var.db_allocated_storage
  storage_type      = "gp3"
  storage_encrypted = true

  # --- ネットワーク(foundation層から取得) ---
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [local.db_sg_id]
  publicly_accessible    = false
  multi_az               = false # 学習用途。本番ならtrueにする判断を書けること

  # --- 認証 ---
  # 復元時(snapshot_identifier指定時)はdb_name/username/passwordは
  # スナップショット側の値が使われ、これらの指定は無視される
  db_name  = var.restore_snapshot_id == null ? var.db_name : null
  username = var.restore_snapshot_id == null ? local.db_creds.username : null
  password = var.restore_snapshot_id == null ? local.db_creds.password : null

  # --- ★ 新規/復元トグルの核 ---
  snapshot_identifier = var.restore_snapshot_id

  # --- ★ destroy時のデータ保全 ---
  skip_final_snapshot       = false
  final_snapshot_identifier = "${var.project}-final-${var.snapshot_suffix}"
  deletion_protection       = false # 学習用途。本番ならtrue

  # --- コスト・運用 ---
  backup_retention_period = 1     # 自動バックアップ最小限(0だとPITR不可)
  apply_immediately       = true  # 学習用途: 変更を即時反映

  lifecycle {
    ignore_changes = [
      # 復元後にsnapshot_identifierをnullに戻してもDBを作り直さない
      snapshot_identifier,
    ]
  }
}
