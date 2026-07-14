terraform {
    required_version = ">=1.8"

    required_providers {
        aws = {
            source = "hashicorp/aws"
            version = "~> 6.0"
        }
        random = {
            source = "hashicorp/random"
            version = "~> 3.6"
        }
    }
}

provider "aws" {
    region = var.aws_region

    default_tags {
        tags = {
            Project = "turbofan-anomaly-detection"
            ManagedBy = "Terraform"
            Layer = "foundation"
        }
    }
}