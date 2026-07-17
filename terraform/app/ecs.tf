# ------------------------------------------------------------
# ECS (クラスタ / タスク定義 / サービス)
#
# 設計判断:
# - DB認証情報は環境変数に平文で置かず、Secrets Managerから
#   コンテナ起動時に注入する(secrets句)。タスク定義のJSONにも残らない
# - CloudWatch Logsの保持期間を明示(無期限だと地味に課金が積もる)
# ------------------------------------------------------------

resource "aws_ecs_cluster" "main" {
  name = "${var.project}-cluster"

  setting {
    name  = "containerInsights"
    value = "disabled" # 有効化は追加課金。学習段階では標準メトリクスで十分
  }
}

resource "aws_cloudwatch_log_group" "api" {
  name              = "/ecs/${var.project}-api"
  retention_in_days = 14
}

resource "aws_ecs_task_definition" "api" {
  family                   = "${var.project}-api"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.task_cpu
  memory                   = var.task_memory
  execution_role_arn       = local.task_execution_role_arn
  task_role_arn            = local.task_role_arn

  # Graviton(ARM)は約2割安いが、イメージをarm64でビルドする必要がある。
  # まずはx86_64で動かし、慣れたらARM化に挑戦するとブログネタになる
  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "X86_64"
  }

  container_definitions = jsonencode([
    {
      name      = "api"
      image     = local.image_uri
      essential = true

      portMappings = [
        {
          containerPort = var.api_port
          protocol      = "tcp"
        }
      ]

      # ★ Secrets Managerからの注入。
      # ARN末尾の「:database_url::」はJSONキー指定(キー名:バージョンステージ:バージョンID)
      secrets = [
        {
          name      = "DATABASE_URL"
          valueFrom = "${local.db_secret_arn}:database_url::"
        }
      ]

      environment = [
        { name = "PORT", value = tostring(var.api_port) }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.api.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "api"
        }
      }
    }
  ])
}

resource "aws_ecs_cluster_capacity_providers" "main" {
  cluster_name       = aws_ecs_cluster.main.name
  capacity_providers = ["FARGATE", "FARGATE_SPOT"]
}

resource "aws_ecs_service" "api" {
  name            = "${var.project}-api"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.api.arn
  desired_count   = var.desired_count

  capacity_provider_strategy {
    capacity_provider = var.use_fargate_spot ? "FARGATE_SPOT" : "FARGATE"
    weight            = 1
  }

  network_configuration {
    subnets          = local.public_subnet_ids
    security_groups  = [local.app_sg_id]
    assign_public_ip = true # NATなし構成の要。ECR pullもこの経路
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.api.arn
    container_name   = "api"
    container_port   = var.api_port
  }

  # PyTorchのモデルロードで起動に時間がかかるため、起動直後の
  # ヘルスチェック失敗でタスクが殺されないよう猶予を設ける。
  # 起動→即停止を繰り返す場合はまずこの値を疑う
  health_check_grace_period_seconds = 120

  # リスナーが先に存在しないとサービス作成が失敗することがある
  depends_on = [aws_lb_listener.http]

  # デプロイのたびにdesired_countの手動変更を上書きしない
  lifecycle {
    ignore_changes = [desired_count]
  }
}
