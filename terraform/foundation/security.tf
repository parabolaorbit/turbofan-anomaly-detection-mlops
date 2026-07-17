# ------------------------------------------------------------
# セキュリティグループ
#
# 設計判断:
# - SG参照チェーンで最小権限を構成する
#   ALB SG --(8080, app層から注入)--> app SG --(5432)--> db SG
# - RDSへの接続元を「CIDR」ではなく「app SGのID」で指定するのが肝。
#   Fargateタスクは起動のたびにIPが変わるが、SG参照なら追従できる
# ------------------------------------------------------------

# --- Fargateタスク用 ---
# ECR pull / Secrets Manager / CloudWatch Logs への到達に必要
resource "aws_security_group" "app" {
    name = "${var.project}-app"
    # nameとdescriptionは変更不可属性。変えるとSGの再作成(destroy→create)になり、
    # 参照元(db SG / タスクのENI)があるとDependencyViolationで失敗する
    description = "Fargate task (FastAPI)"
    vpc_id = aws_vpc.main.id

    tags = {
        Name = "${var.project}-app-sg"
    }
}

# ECR pull / Secrets Manager / CloudWatch Logs への到達に必要
resource "aws_vpc_security_group_egress_rule" "app_all_outbound" {
    security_group_id = aws_security_group.app.id
    description = "Allow all outbound traffic"
    ip_protocol = "-1"
    cidr_ipv4 = "0.0.0.0/0"
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