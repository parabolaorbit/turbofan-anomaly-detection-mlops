# ------------------------------------------------------------
# ECR (コンテナレジストリ)
#
# 設計判断:
# - PyTorch込みのイメージは1つ数GBになる。放置するとストレージ課金
#   ($0.10/GB/月)が積み上がるため、ライフサイクルポリシーで直近5世代のみ保持
# ------------------------------------------------------------

resource "aws_ecr_repository" "api" {
    name = "${var.project}-api"
    image_tag_mutability = "MUTABLE"

    image_scanning_configuration {
        scan_on_push = true # 脆弱性スキャン
    }

    # 学習用途: destroy時にイメージが残っていても強制削除
    force_delete = true
}

resource "aws_ecr_lifecycle_policy" "api" {
    repository = aws_ecr_repository.api.name

    policy = jsonencode({
        rules = [
            {
                rulePriority = 1
                description = "Keep only the last 5 images"
                selection = {
                    tagStatus = "any"
                    countType = "imageCountMoreThan"
                    countNumber = 5
                }
                action = {
                    type = "expire"
                }
            }
        ]
    })
}