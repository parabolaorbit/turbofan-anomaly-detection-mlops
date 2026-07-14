# ------------------------------------------------------------
# Outputs + SSM Parameter Store書き出し
#
# 設計判断:
# - data層/app層への値の受け渡しは SSM Parameter Store 経由にする
#   - terraform_remote_state方式より疎結合(下位層がstateファイルの
#     置き場所や内部構造を知らなくてよい)
#   - Standardパラメータは無料
# - 下位層は data "aws_ssm_parameter" で読むだけ
# ------------------------------------------------------------
locals {
    ssm_prefix = "/${var.project}/foundation"
}

resource "aws_ssm_parameter" "vpc_id" {
  name  = "${local.ssm_prefix}/vpc_id"
  type  = "String"
  value = aws_vpc.main.id
}

resource "aws_ssm_parameter" "public_subnet_ids" {
  name  = "${local.ssm_prefix}/public_subnet_ids"
  type  = "StringList"
  value = join(",", aws_subnet.public[*].id)
}

resource "aws_ssm_parameter" "private_subnet_ids" {
  name  = "${local.ssm_prefix}/private_subnet_ids"
  type  = "StringList"
  value = join(",", aws_subnet.private[*].id)
}

resource "aws_ssm_parameter" "app_sg_id" {
  name  = "${local.ssm_prefix}/app_sg_id"
  type  = "String"
  value = aws_security_group.app.id
}

resource "aws_ssm_parameter" "db_sg_id" {
  name  = "${local.ssm_prefix}/db_sg_id"
  type  = "String"
  value = aws_security_group.db.id
}

resource "aws_ssm_parameter" "ecr_repository_url" {
  name  = "${local.ssm_prefix}/ecr_repository_url"
  type  = "String"
  value = aws_ecr_repository.api.repository_url
}

resource "aws_ssm_parameter" "task_execution_role_arn" {
  name  = "${local.ssm_prefix}/task_execution_role_arn"
  type  = "String"
  value = aws_iam_role.task_execution.arn
}

resource "aws_ssm_parameter" "task_role_arn" {
  name  = "${local.ssm_prefix}/task_role_arn"
  type  = "String"
  value = aws_iam_role.task.arn
}

resource "aws_ssm_parameter" "db_master_secret_arn" {
  name  = "${local.ssm_prefix}/db_master_secret_arn"
  type  = "String"
  value = aws_secretsmanager_secret.db_master.arn
}

# --- CLI確認用のoutputs ---
output "vpc_id" {
    value = aws_vpc.main.id
}

output "repository_url" {
    value = aws_ecr_repository.api.repository_url
}

output "ssm_prefix" {
    description = "SSM Parameter Store prefix"
    value = local.ssm_prefix
}