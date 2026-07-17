# Terraform 運用手順

3層構成。**apply は foundation → data → app、destroy は逆順(app → data)**。
下位層は上位層の SSM パラメータを plan 時に読むため、順序は実行時に強制される。

| 層 | 内容 | ライフサイクル | 放置時のコスト |
|---|---|---|---|
| `foundation/` | VPC / サブネット / SG / ECR / IAM / マスターシークレット / SSM | 常設(destroy しない) | ほぼ $0(シークレット $0.40/月 + ECR イメージ分) |
| `data/` | RDS PostgreSQL / 接続用シークレット | 使う期間だけ | 稼働中 約 $15〜20/月。destroy 後はスナップショット数十円のみ |
| `app/` | ECS クラスタ / タスク定義 / サービス / ALB / ログ | デモ・開発時だけ | 稼働中 ALB 約 $0.55/日 + Fargate Spot 微額。destroy 後 $0 |

---

## 起動(apply)

### 0. 前提

- イメージが ECR にあること(main へ push すれば CI が `turbofan-api:latest` を投入する)
- foundation を apply する場合のみ、DB マスター認証情報を環境変数で渡す:

```powershell
$env:TF_VAR_db_username = "<ユーザー名>"
$env:TF_VAR_db_password = "<パスワード>"
```

※ data / app の apply には不要(認証情報は foundation のシークレット経由)。

### 1. foundation(通常は変更がある時だけ)

```powershell
terraform -chdir=terraform/foundation apply
```

### 2. data — 新規 or スナップショット復元

```powershell
# 空のDBを新規作成
terraform -chdir=terraform/data apply

# 前回の最終スナップショットから復元(データ引き継ぎ)
terraform -chdir=terraform/data apply -var "restore_snapshot_id=turbofan-final-<サフィックス>"
```

利用可能なスナップショットの確認:

```powershell
aws rds describe-db-snapshots --query "DBSnapshots[?starts_with(DBSnapshotIdentifier,'turbofan-final')].[DBSnapshotIdentifier,SnapshotCreateTime]" --output table
```

RDS 起動に 5〜10 分かかる。

### 3. app

```powershell
terraform -chdir=terraform/app apply
```

- API の URL は output `api_url`(ALB の DNS 名)に出る。
- マイグレーションは API コンテナが起動時に `alembic upgrade head` を実行するため通常は不要。
  単発で流したい場合(README 下部「マイグレーションの単発実行」参照)。

### 4. 動作確認

```powershell
terraform -chdir=terraform/app output -raw api_url
curl "$(terraform -chdir=terraform/app output -raw api_url)/"
```

タスクが起動しない時は CloudWatch Logs `/ecs/turbofan-api` を確認。

---

## 停止(destroy)

**順序厳守: app → data。foundation は destroy しない。**

```powershell
# 1. app
terraform -chdir=terraform/app destroy

# 2. data(最終スナップショット名をユニークにするため -var 必須)
terraform -chdir=terraform/data destroy -var "snapshot_suffix=$(Get-Date -Format yyyyMMddHHmm)"
```

- 作成されるスナップショット名は `turbofan-final-<サフィックス>`。**次回復元用にメモする**
  (忘れても上記 describe-db-snapshots で確認できる)。
- `-var` を忘れてデフォルト名(`turbofan-final-manual`)が衝突すると destroy が失敗する。
  その場合はユニークな値を付けて再実行。
- destroy 中・destroy 後に main へ push しても CI は正常終了する
  (サービス不在時はデプロイをスキップする設計)。

### destroy 後の確認(任意)

```powershell
aws rds describe-db-instances --query 'DBInstances[*].DBInstanceIdentifier'  # 空ならOK
aws ecs list-clusters                                                        # 空ならOK
aws elbv2 describe-load-balancers --query 'LoadBalancers[*].LoadBalancerName' # 空ならOK
```

---

## 開発集中期(数日 DB を残す場合)

app だけ destroy して data は残す運用も可(RDS 約 $0.6/日)。
翌日は `terraform -chdir=terraform/app apply` だけで再開できる。

---

## マイグレーションの単発実行

API コンテナ起動時に自動実行されるが、手動で流す場合:

```powershell
$SUBNETS = (aws ssm get-parameter --name /turbofan/foundation/public_subnet_ids --query Parameter.Value --output text)
$SG      = (aws ssm get-parameter --name /turbofan/foundation/app_sg_id --query Parameter.Value --output text)
aws ecs run-task `
  --cluster turbofan-cluster `
  --launch-type FARGATE `
  --task-definition turbofan-migrate `
  --network-configuration "awsvpcConfiguration={subnets=[$SUBNETS],securityGroups=[$SG],assignPublicIp=ENABLED}"
```

ログは `/ecs/turbofan-migrate`。

---

## 完全撤収(プロジェクト終了時のみ)

```powershell
terraform -chdir=terraform/app destroy
terraform -chdir=terraform/data destroy -var "snapshot_suffix=final"
terraform -chdir=terraform/foundation destroy   # ECRはイメージごと消える(force_delete)
```

- マスターシークレットは 7 日間の削除猶予後に完全削除される。
- 残った RDS スナップショットは不要なら手動削除:
  `aws rds delete-db-snapshot --db-snapshot-identifier <名前>`

---

## よくあるエラー

| 症状 | 原因と対処 |
|---|---|
| data/app の plan で SSM パラメータが見つからない | 上位層が未 apply。foundation → data → app の順で |
| destroy が最終スナップショット名の衝突で失敗 | `-var "snapshot_suffix=..."` にユニーク値を渡す |
| タスクが `CannotPullContainerError` | ECR にイメージがない。main へ push して CI を実行 |
| タスクが `Essential container exited` | `/ecs/turbofan-api` のログを確認(DB接続・依存関係が典型) |
| foundation apply で変数入力を求められる | `TF_VAR_db_username` / `TF_VAR_db_password` を設定 |
