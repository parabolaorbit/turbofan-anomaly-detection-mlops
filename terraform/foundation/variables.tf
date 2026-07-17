variable "aws_region" {
    description = "AWS Region"
    type = string
    default = "ap-northeast-1"
}

variable "project" {
    description = "Project name"
    type = string
    default = "turbofan"
}

variable "vpc_cidr" {
    description = "VPC CIDR"
    type = string
    default = "10.0.0.0/16"
}

variable "db_username" {
  description = "マスターユーザー名"
  type        = string
  default     = "turbofan_admin"
}

variable "db_password" {
  description = "マスターパスワード"
  type        = string
  default     = "turbofan_admin_pass"
}