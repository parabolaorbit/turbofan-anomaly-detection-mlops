variable "aws_region" {
  description = "デプロイ先リージョン"
  type        = string
  default     = "ap-northeast-1"
}

variable "project" {
  description = "リソース名のプレフィックス(他層と揃えること)"
  type        = string
  default     = "turbofan"
}

# デプロイするイメージのタグ。latest運用は「どのコードが動いているか」が
# 追えなくなるため、gitのコミットハッシュ等を渡す運用を推奨
# 例: terraform apply -var="image_tag=$(git rev-parse --short HEAD)"
variable "image_tag" {
  description = "ECR上のイメージタグ"
  type        = string
  default     = "latest"
}

variable "api_port" {
  description = "FastAPIコンテナのポート(docker/DockerfileのCMDが8000固定のため揃えること)"
  type        = number
  default     = 8000
}

# Fargateの有効なCPU/メモリ組み合わせに注意:
#   512(0.5vCPU) → 1024〜4096MB / 1024(1vCPU) → 2048〜8192MB
# PyTorchのモデルロードでメモリ不足になったら2048→4096に上げる
variable "task_cpu" {
  description = "タスクCPUユニット"
  type        = number
  default     = 512
}

variable "task_memory" {
  description = "タスクメモリ(MB)"
  type        = number
  default     = 2048
}

variable "desired_count" {
  description = "APIタスクの起動数"
  type        = number
  default     = 1
}

variable "alb_allowed_cidrs" {
  description = "ALBのIngress許可CIDRリスト"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "health_check_path" {
  description = "ALBのヘルスチェックパス(api/main.pyの `GET /` がヘルスチェック実装)"
  type        = string
  default     = "/"
}

# Fargate Spot: 約7割引だが中断されうる。学習・デモ用途ならtrue推奨
variable "use_fargate_spot" {
  description = "Fargate Spotを使うか"
  type        = bool
  default     = true
}

# --- HTTPS関連 ---
# 証明書とホストゾーンはコンソールで作成済みの長寿命リソース。
# Terraform管理外なので、ARN/IDを変数で受け取る(terraform.tfvarsに記載)

variable "domain_name" {
  description = "APIの公開ドメイン名(ACM証明書のドメインと一致させること)"
  type        = string
  default     = "turbofan-api.parabolaorbit-dev.net"
}

variable "certificate_arn" {
  description = "ACM証明書のARN(ALBと同一リージョンで発行済み・ISSUED状態であること)"
  type        = string
}

variable "hosted_zone_id" {
  description = "Route53ホストゾーンID(parabolaorbit-dev.net)"
  type        = string
}
