# ------------------------------------------------------------
# Outputs + SSM Parameter Store書き出し
#
# app層はこれらのSSMパラメータを読んでタスク定義を組み立てる
# ------------------------------------------------------------

locals {
  ssm_out_prefix = "/${var.project}/data"
}

resource "aws_ssm_parameter" "db_endpoint" {
  name  = "${local.ssm_out_prefix}/db_endpoint"
  type  = "String"
  value = aws_db_instance.main.address
}

resource "aws_ssm_parameter" "db_secret_arn" {
  name  = "${local.ssm_out_prefix}/db_secret_arn"
  type  = "String"
  value = aws_secretsmanager_secret.db.arn
}

output "db_endpoint" {
  value = aws_db_instance.main.address
}

output "db_secret_arn" {
  description = "app層のタスク定義でsecretsとして注入する"
  value       = aws_secretsmanager_secret.db.arn
}

output "final_snapshot_name_on_destroy" {
  description = "destroy時に作成されるスナップショット名(復元時にこれを指定)"
  value       = "${var.project}-final-${var.snapshot_suffix}"
}
