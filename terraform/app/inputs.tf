# ------------------------------------------------------------
# foundation層・data層からの入力(SSM Parameter Store経由)
#
# app層は両方の層に依存する。どちらかが未applyならここで止まるため、
# 「foundation → data → app」の順序が実行時に強制される
# ------------------------------------------------------------

locals {
  ssm_foundation = "/${var.project}/foundation"
  ssm_data       = "/${var.project}/data"
}

# --- foundation層 ---
data "aws_ssm_parameter" "public_subnet_ids" {
  name = "${local.ssm_foundation}/public_subnet_ids"
}

data "aws_ssm_parameter" "app_sg_id" {
  name = "${local.ssm_foundation}/app_sg_id"
}

data "aws_ssm_parameter" "ecr_repository_url" {
  name = "${local.ssm_foundation}/ecr_repository_url"
}

data "aws_ssm_parameter" "task_execution_role_arn" {
  name = "${local.ssm_foundation}/task_execution_role_arn"
}

data "aws_ssm_parameter" "task_role_arn" {
  name = "${local.ssm_foundation}/task_role_arn"
}

# --- data層 ---
data "aws_ssm_parameter" "db_secret_arn" {
  name = "${local.ssm_data}/db_secret_arn"
}

locals {
  public_subnet_ids       = split(",", data.aws_ssm_parameter.public_subnet_ids.value)
  app_sg_id               = data.aws_ssm_parameter.app_sg_id.value
  ecr_repository_url      = data.aws_ssm_parameter.ecr_repository_url.value
  task_execution_role_arn = data.aws_ssm_parameter.task_execution_role_arn.value
  task_role_arn           = data.aws_ssm_parameter.task_role_arn.value
  db_secret_arn           = data.aws_ssm_parameter.db_secret_arn.value

  image_uri = "${local.ecr_repository_url}:${var.image_tag}"
}
