# ------------------------------------------------------------
# ネットワーク基盤
#
# 設計判断:
# - NAT Gatewayは使わない(月$35の固定費を回避)
# - Fargateタスクはパブリックサブネットに配置し、パブリックIP経由で
#   ECR/インターネットへ到達する(SGでインバウンドを絞って防御)
# - RDSはプライベートサブネットに配置。NATがなくてもVPC内ルーティングで
#   Fargate→RDSは疎通する(アウトバウンド不要なDBにNATは不要)
# - プライベートサブネットが2AZ必要なのは、RDSのDB Subnet Groupが
#   2AZ以上を要求するため(Single-AZインスタンスでも要求される)
# ------------------------------------------------------------

data "aws_availability_zones" "available" {
  state = "available"
}

resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "${var.project}-vpc"
  }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${var.project}-igw"
  }
}

# --- パブリックサブネット x2 (Fargate用) ---
resource "aws_subnet" "public" {
  count = 2

  vpc_id                  = aws_vpc.main.id
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, count.index) # 10.0.0.0/24, 10.0.1.0/24
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name = "${var.project}-public-${count.index}"
  }
}

# --- プライベートサブネット x2 (RDS用) ---
resource "aws_subnet" "private" {
  count = 2

  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index + 10) # 10.0.10.0/24, 10.0.11.0/24
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name = "${var.project}-private-${count.index}"
  }
}

# --- ルーティング ---
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "${var.project}-public-rt"
  }
}

resource "aws_route_table_association" "public" {
  count = 2

  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# プライベートサブネットはVPCデフォルトのローカルルートのみ
# (外向き経路なし = RDSはインターネットから完全に隔離される)
resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${var.project}-private-rt"
  }
}

resource "aws_route_table_association" "private" {
  count = 2

  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private.id
}
