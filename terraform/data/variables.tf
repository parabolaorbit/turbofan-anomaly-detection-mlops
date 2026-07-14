variable "aws_region" {
  description = "デプロイ先リージョン"
  type        = string
  default     = "ap-northeast-1"
}

variable "project" {
  description = "リソース名のプレフィックス(foundation層と揃えること)"
  type        = string
  default     = "turbofan"
}

# ------------------------------------------------------------
# ★ この層の運用の核となるトグル
#
# 新規作成:           restore_snapshot_id = null (デフォルト)
# スナップショット復元: terraform apply -var="restore_snapshot_id=turbofan-final-YYYYMMDDHHMM"
#
# 利用可能なスナップショットの確認:
#   aws rds describe-db-snapshots \
#     --query "DBSnapshots[?starts_with(DBSnapshotIdentifier,'turbofan-final')].[DBSnapshotIdentifier,SnapshotCreateTime]" \
#     --output table
# ------------------------------------------------------------
variable "restore_snapshot_id" {
  description = "復元元スナップショットID。nullなら空のDBを新規作成"
  type        = string
  default     = null
}

# destroy時に自動作成される最終スナップショットの識別子サフィックス。
# 同名スナップショットが既に存在するとdestroyが失敗するため、毎回ユニークにする。
# 運用例: terraform destroy -var="snapshot_suffix=$(date +%Y%m%d%H%M)"
variable "snapshot_suffix" {
  description = "最終スナップショット名のサフィックス(destroy時にユニーク値を渡す)"
  type        = string
  default     = "manual"
}

variable "db_name" {
  description = "データベース名"
  type        = string
  default     = "anomaly"
}

variable "db_instance_class" {
  description = "インスタンスクラス(t4g.microは無料枠対象)"
  type        = string
  default     = "db.t4g.micro"
}

variable "db_allocated_storage" {
  description = "ストレージ(GB)。20GBまで無料枠対象"
  type        = number
  default     = 20
}
