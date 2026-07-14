# ------------------------------------------------------------
# Outputs
#
# FargateタスクのパブリックIPは起動ごとに変わり、Terraformの
# apply時点では確定しない(サービスが後からタスクを起動するため)。
# そのためIP取得はCLIで行う。コマンドをoutputとして出力しておく
# ------------------------------------------------------------

output "cluster_name" {
  value = aws_ecs_cluster.main.name
}

output "migrate_task_family" {
  value = aws_ecs_task_definition.migrate.family
}

output "how_to_get_public_ip" {
  description = "APIタスクのパブリックIPを取得するコマンド"
  value       = <<-EOT
    TASK_ARN=$(aws ecs list-tasks --cluster ${aws_ecs_cluster.main.name} --service-name ${aws_ecs_service.api.name} --query 'taskArns[0]' --output text)
    ENI_ID=$(aws ecs describe-tasks --cluster ${aws_ecs_cluster.main.name} --tasks $TASK_ARN --query 'tasks[0].attachments[0].details[?name==`networkInterfaceId`].value' --output text)
    aws ec2 describe-network-interfaces --network-interface-ids $ENI_ID --query 'NetworkInterfaces[0].Association.PublicIp' --output text
  EOT
}
