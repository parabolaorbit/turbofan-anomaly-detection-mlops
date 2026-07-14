# ------------------------------------------------------------
# foundation層からの入力
#
# SSM Parameter Store経由で読む(疎結合)。
# foundation層が未applyだとここでエラーになる。
# → 「foundationが先」という依存関係が実行時に自然と強制される
# ------------------------------------------------------------

locals {
  ssm_prefix = "/${var.project}/foundation"
}

data "aws_ssm_parameter" "private_subnet_ids" {
  name = "${local.ssm_prefix}/private_subnet_ids"
}

data "aws_ssm_parameter" "db_sg_id" {
  name = "${local.ssm_prefix}/db_sg_id"
}

data "aws_ssm_parameter" "task_execution_role_arn" {
  name = "${local.ssm_prefix}/task_execution_role_arn"
}

locals {
  private_subnet_ids = split(",", data.aws_ssm_parameter.private_subnet_ids.value)
  db_sg_id           = data.aws_ssm_parameter.db_sg_id.value
}
