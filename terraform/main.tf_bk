terraform {
    required_version = ">= 1.0"
}

provider "aws" {
    region = "ap-northeast-1"
}

resource "aws_ecr_repository" "anomaly_api" {
    name="turbofan-anomaly-api"
}

resource "aws_db_instance" "postgres" {
    identifier = "anomaly-db"

    engine = "postgres"

    instance_class = "db.t3.micro"

    allocated_storage = 20
}