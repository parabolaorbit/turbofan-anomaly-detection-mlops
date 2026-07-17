# ------------------------------------------------------------
# ALB (Application Load Balancer)
#
# 設計判断:
# - ALBはapp層と同じ「使い捨て」ライフサイクルなので、この層に置く。
#   ALB用SGもここに置き、foundation層は一切変更しない
# - foundation側のapp SGへの「ALBからの許可」も、この層から
#   aws_vpc_security_group_ingress_rule で注入する
#   → destroyすればルールごと消え、foundationは元の状態に戻る
# - リスナーはHTTP:80。HTTPS化はACM証明書+独自ドメイン取得後の
#   改善ステップとして分離(下部コメント参照)
#
# コスト: 約$0.0225/時 + LCU。使い捨て運用なら1日デモで$0.2前後
# ------------------------------------------------------------

# --- ALB用SG ---
resource "aws_security_group" "alb" {
  name        = "${var.project}-alb-sg"
  description = "ALB for turbofan API"
  vpc_id      = data.aws_ssm_parameter.vpc_id.value

  ingress {
    description = "HTTP from allowed CIDRs"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = var.alb_allowed_cidrs
  }

  egress {
    description = "To targets"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project}-alb-sg"
  }
}

# --- foundation層のapp SGに「ALBからのみ許可」を注入 ---
# 既存のapp SG本体には触らず、ルールだけを別リソースとして追加する。
# app層をdestroyすればこのルールも消える
resource "aws_vpc_security_group_ingress_rule" "app_from_alb" {
  security_group_id            = local.app_sg_id
  description                  = "API port from ALB only"
  from_port                    = var.api_port
  to_port                      = var.api_port
  ip_protocol                  = "tcp"
  referenced_security_group_id = aws_security_group.alb.id
}

# --- ALB本体 ---
resource "aws_lb" "main" {
  name               = "${var.project}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = local.public_subnet_ids # 2AZ必須(foundationで確保済み)
}

# --- ターゲットグループ ---
resource "aws_lb_target_group" "api" {
  # 固定名だとポート等の変更時に「リスナー使用中で削除不可」になるため、
  # name_prefix + create_before_destroy で新旧を入れ替える(prefixは最大6文字)
  name_prefix = "tf-api"
  port        = var.api_port
  protocol    = "HTTP"
  vpc_id      = data.aws_ssm_parameter.vpc_id.value
  target_type = "ip" # ★ Fargate(awsvpcモード)では"ip"必須。"instance"だと登録できない

  # デモ用途: タスク入れ替え時の待ち時間を短縮(デフォルト300秒)
  deregistration_delay = 30

  health_check {
    path                = var.health_check_path
    matcher             = "200"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 3
  }

  lifecycle {
    create_before_destroy = true
  }
}

# --- リスナー(HTTP) ---
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.api.arn
  }
}

# ------------------------------------------------------------
# HTTPS化する場合(独自ドメイン+ACM証明書の取得後):
#
# 1. aws_acm_certificate + Route53でDNS検証
# 2. aws_lb_listener "https" (port=443, protocol="HTTPS",
#    certificate_arn=..., ssl_policy="ELBSecurityPolicy-TLS13-1-2-2021-06")
# 3. 上のHTTPリスナーのdefault_actionを redirect(301→443)に変更
# ------------------------------------------------------------
