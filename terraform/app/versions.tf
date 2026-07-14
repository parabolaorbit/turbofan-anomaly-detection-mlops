terraform {
  required_version = ">= 1.7"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # S3バックエンド移行時のkey: turbofan/app/terraform.tfstate
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project   = "turbofan-anomaly-detection"
      ManagedBy = "terraform"
      Layer     = "app"
    }
  }
}
