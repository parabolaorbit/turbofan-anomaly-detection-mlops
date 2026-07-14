terraform {
  required_version = ">= 1.7"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # foundation層と同様、学習初期はローカルstateでOK。
  # S3バックエンドに移行する場合はkeyを層ごとに分ける:
  #   turbofan/foundation/terraform.tfstate
  #   turbofan/data/terraform.tfstate
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project   = "turbofan-anomaly-detection"
      ManagedBy = "terraform"
      Layer     = "data"
    }
  }
}
