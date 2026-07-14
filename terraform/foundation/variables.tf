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

# Fargateタスク(API)への接続を許可するCIDR。
variable "api_allowed_cidrs" {
    description = "CIDR to allow access to API"
    type = list(string)
    default = ["60.151.193.119/32"]
}

variable "api_port" {
    description = "Port to allow access to API"
    type = number
    default = 8080
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