# ------------------------------------------------------------
# DBマイグレーション用ワンショットタスク
#
# 背景:
#   RDSはプライベートサブネットにあり、手元PCから直接
#   alembic upgrade head を実行できない。
#
# 解決策:
#   同じアプリイメージを使い、コマンドだけalembicに差し替えた
#   タスク定義を用意。必要な時に aws ecs run-task で単発実行する。
#   踏み台EC2を立てるより安く(実行した数分だけ課金)、
#   「マイグレーションも本番と同じネットワーク経路で流す」ため
#   本番運用のパターンとしてもそのまま通用する
#
# 実行コマンドはREADME参照
# ------------------------------------------------------------

resource "aws_cloudwatch_log_group" "migrate" {
  name              = "/ecs/${var.project}-migrate"
  retention_in_days = 14
}

resource "aws_ecs_task_definition" "migrate" {
  family                   = "${var.project}-migrate"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 256 # マイグレーションは軽量でよい
  memory                   = 512
  execution_role_arn       = local.task_execution_role_arn
  task_role_arn            = local.task_role_arn

  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "X86_64"
  }

  container_definitions = jsonencode([
    {
      name      = "migrate"
      image     = local.image_uri
      essential = true

      # アプリと同じイメージで、実行コマンドだけ差し替える
      command = ["alembic", "upgrade", "head"]

      secrets = [
        {
          name      = "DATABASE_URL"
          valueFrom = "${local.db_secret_arn}:database_url::"
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.migrate.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "migrate"
        }
      }
    }
  ])
}
