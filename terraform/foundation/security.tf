# ------------------------------------------------------------
# セキュリティグループ
#
# 設計判断:
# - SG参照チェーンで最小権限を構成する
#   インターネット --(8080, 許可CIDRのみ)--> app SG --(5432)--> db SG
# - RDSへの接続元を「CIDR」ではなく「app SGのID」で指定するのが肝。
#   Fargateタスクは起動のたびにIPが変わるが、SG参照なら追従できる
# ------------------------------------------------------------

# --- Fargateタスク用 ---
resource "aws_security_group" "app" {
    name = "${var.project}-app"
    description = "Fargate task (FastAPI)"
    vpc_id = aws_vpc.main.id

    ingress {
        description = "API access"
        from_port = var.api_port
        to_port = var.api_port
        protocol = "tcp"
        cidr_blocks = var.api_allowed_cidrs
    }

    # ECR pull / Secrets Manager / CloudWatch Logs への到達に必要
    egress {
        description = "Allow all outbound traffic"
        from_port = 0
        to_port = 0
        protocol = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }

    tags = {
        Name = "${var.project}-app-sg"
    }
}

# --- RDS用 ---
resource "aws_security_group" "db" {
    name = "${var.project}-db-sg"
    description = "RDS (PostgreSQL)"
    vpc_id = aws_vpc.main.id

    ingress {
        description = "PostgreSQL from app tasks only"
        from_port = 5432
        to_port = 5432
        protocol = "tcp"
        security_groups = [aws_security_group.app.id] #SG参照。CIDRではない
    }

    # DBからのアウトバウンドは不要(応答トラフィックはステートフルに許可される)
    # egressブロックを書かない = アウトバウンド全拒否

    tags = {
        Name = "${var.project}-db-sg"
    }
}