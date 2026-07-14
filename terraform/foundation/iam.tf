# ------------------------------------------------------------
# IAM (ECS用ロール)
#
# 設計判断:
# - 「実行ロール」と「タスクロール」を明確に分離する
#   - execution role: ECSエージェントが使う(ECR pull, ログ出力, シークレット注入)
#   - task role:      アプリのコード自身が使う(現時点では権限なし)
#   この区別はECSで最初に混乱するポイントなので、名前とコメントで明示する
# - Secrets Managerへのアクセス許可は、シークレット自体を作るdata層で
#   ARNを特定してからポリシーを追加する(ここでは土台のロールのみ)
# ------------------------------------------------------------
data "aws_iam_policy_document" "ecs_task_assume" {
    statement {
        actions = ["sts:AssumeRole"]

        principals {
            type = "Service"
            identifiers = ["ecs-tasks.amazonaws.com"]
        }
    }
}


# --- タスク実行ロール(ECSエージェント用) ---
resource "aws_iam_role" "task_execution" {
    name = "${var.project}-EcsTaskExecutionRole"

    assume_role_policy = data.aws_iam_policy_document.ecs_task_assume.json
}

resource "aws_iam_role_policy_attachment" "task_execution_managed" {
    role       = aws_iam_role.task_execution.name
    policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# --- タスクロール(アプリケーション用) ---
resource "aws_iam_role" "task" {
    name = "turbofan-EcsTaskRole"

    assume_role_policy = data.aws_iam_policy_document.ecs_task_assume.json
}