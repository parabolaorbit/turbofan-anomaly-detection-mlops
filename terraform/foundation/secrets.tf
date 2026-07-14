# マスター認証情報。foundationと共に生き、destroyされない
resource "aws_secretsmanager_secret" "db_master" {
  name                    = "${var.project}/db-master"
  recovery_window_in_days = 7
}

resource "aws_secretsmanager_secret_version" "db_master" {
  secret_id = aws_secretsmanager_secret.db_master.id
  secret_string = jsonencode({
    username = var.db_username
    password = var.db_password
  })
}