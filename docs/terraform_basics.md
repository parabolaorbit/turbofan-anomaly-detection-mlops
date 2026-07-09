## Result

- Imported existing ECR repository into Terraform state.
- Enabled image scan on push.
- Confirmed no drift with `terraform plan`.

## Commands

terraform import aws_ecr_repository.api turbofan-anomaly-api
terraform apply
terraform plan