resource "aws_ecr_repository" "api" {
    name = "turbofan-anomaly-api"

    image_scanning_configuration {
        scan_on_push = true
    }

    image_tag_mutability = "MUTABLE"
}