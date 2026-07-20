# Turbofan Anomaly Detection MLOps Platform
![Python](https://img.shields.io/badge/Python-3.11-blue)
![PyTorch](https://img.shields.io/badge/PyTorch-LSTM_AutoEncoder-red)
![FastAPI](https://img.shields.io/badge/FastAPI-REST_API-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED)
![MLflow](https://img.shields.io/badge/MLflow-Tracking-0194E2?logo=mlflow&logoColor=white)
![Prometheus](https://img.shields.io/badge/Prometheus-Monitoring-E6522C?logo=prometheus&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-Dashboard-F46800?logo=grafana&logoColor=white)
![Terraform](https://img.shields.io/badge/Terraform-IaC-844FBA?logo=terraform&logoColor=white)
![GitHubActions](https://img.shields.io/badge/GitHub_Actions-CI-2088FF?logo=githubactions&logoColor=white)

NASA turbofan engine degradationシミュレーション向けの
LSTM AutoEncoderによる異常検知システムです。

単なる機械学習モデルではなく、下記を統合した MLOps プラットフォームとして構築しています。

- FastAPI API
- PostgreSQL
- MLflow Model Registry
- Prometheus
- Grafana
- Streamlit Dashboard
- Docker
- GitHub Actions
- Terraform
- AWS Deployment


## Overview

- 入力: エンジンごとの時系列センサーデータ(unit_number / time_in_cycles / ope_setting1-3 / sensor_ms1-21)
- モデル: LSTM AutoEncoder
- 推論: 再構成誤差を anomaly score として算出
- API: FastAPI `/predict`, `/predict_batch`(ヘルスチェック: `GET /`、メトリクス: `GET /metrics`)
  ※ `/predict`・`/predict_batch` は `X-API-Key` ヘッダー必須・レート制限 5 req/min
- ログ: SQLAlchemy 経由で `prediction_logs` テーブルに保存
  (接続先は `DATABASE_URL`。デフォルトは `sqlite:///./anomaly.db`、Docker/CI では PostgreSQL を想定)
- 実行環境: Docker / Docker Compose / WSL

構成図は [architecture_v2.md](docs/architecture_v2.md) を参照してください。

## Features

- Input: engine sensor time-series
- Model: LSTM AutoEncoder による再構成誤差ベースの異常検知
- 推論: ローリング平均誤差 + 連続アラート判定で False Positive を抑制
- API: FastAPI `/predict` および `/predict_batch` エンドポイント
- Database: PostgreSQL + SQLAlchemy ORM + Alembic マイグレーション
- ログ: 予測結果を PostgreSQL に永続化 
- Migration: Alembic
- 監視:  Streamlit ダッシュボードで Severity・異常スコア・レイテンシを可視化
- デプロイ: Docker Compose でワンコマンド起動
- CI: GitHub Actions + pytest (PostgreSQL サービスコンテナ使用) 
- CD: GitHub Actions で ECR へイメージを push し、ECS サービスを再デプロイ(main ブランチ push 時)

## Dashboard

![Dashboard](docs/dashboard.png)

このダッシュボードは監視メトリクス、Severity、異常値スコアのトレンド、直近ログを可視化します。

```bash
streamlit run scripts/dashboard.py
```

## MLOps / Operational Design

このプロジェクトでは、モデル学習に加えAIシステムの運用を設計しました。

- prediction logging
- monitoring metrics
- drift monitoring(`scripts/retraining_decision.py`: sensor_ms2 のドリフト比率を監視)
- retraining decision support(alert率・平均スコア・ドリフトから NO_ACTION / WATCH / REVIEW を判定)
- dashboard visualization
- Dockerized deployment
- CI による回帰テスト

## Tech Stack

### ML
- PyTorch
- Scikit-Learn

### API
- FastAPI
- Pydantic

### Database
- PostgreSQL
- SQLAlchemy
- Alembic

### Monitoring
- Prometheus
- Grafana
- Streamlit

### MLOps
- MLflow
- APScheduler

### DevOps
- Docker
- GitHub Actions
- Terraform
- AWS


## Project Structure

```text
.
├── api/
│   ├── main.py                 # FastAPI アプリ・ルーター定義(lifespan でモデル読込)
│   └── api_model.py            # Pydantic リクエストモデル (SensorRecord / PredictRequest)
├── core/
│   ├── config.py               # pydantic-settings による設定管理 (.env / 環境変数)
│   ├── security.py             # API Key 認証 (X-API-Key ヘッダー検証)
│   ├── const.py                # OpenAPI レスポンス例などの定数定義
│   ├── exceptions.py           # レート制限・内部エラーの例外ハンドラ
│   └── logging_config.py       # 構造化ログ設定
├── monitoring/
│   └── metrics.py              # Prometheus メトリクス定義 (prediction_latency_seconds)
├── db/
│   ├── database.py             # SQLAlchemy エンジン・セッション
│   ├── models.py               # PredictionLog ORM モデル
│   └── crud.py                 # (旧) 関数ベースの DB アクセス
├── repositories/
│   └── prediction_log_repository.py  # DB アクセス層
├── services/
│   └── prediction_service.py   # 推論ビジネスロジック
├── src/
│   ├── model.py                # LSTM AutoEncoder 定義
│   ├── train.py                # モデル学習スクリプト (CLI 引数対応)
│   ├── inference.py            # 前処理・推論・アラート判定
│   ├── dataset.py              # データロード・シーケンス生成
│   ├── metrics.py              # 再構成誤差計算
│   ├── utils.py                # ロギング初期化などの共通ユーティリティ
│   ├── dashboard.py            # (旧) 簡易 Streamlit UI
│   ├── prediction_logger.py    # (旧) JSONL ログ
│   └── sqlite_logger.py        # (旧) SQLite 直書きログ
├── scripts/
│   ├── dashboard.py            # Streamlit 監視ダッシュボード
│   ├── batch_predict.py        # CSV バッチ推論
│   ├── retraining_decision.py  # 再学習要否の自動判断
│   ├── retrain.py              # 再学習実行スクリプト
│   ├── scheduler.py            # APScheduler による定期再学習
│   └── test_api_manual.py      # 手動 API テスト
├── alembic/                    # DB マイグレーション (alembic.ini はルート)
├── docker/
│   ├── docker-compose.yml      # anomaly-api + anomaly-db + prometheus + grafana
│   ├── Dockerfile
│   └── prometheus/             # Prometheus 設定 (prometheus.yml)
├── terraform/                  # AWS インフラ定義 (3層構成、運用手順は terraform/README.md)
│   ├── foundation/             # VPC / SG / ECR / IAM / シークレット (常設)
│   ├── data/                   # RDS PostgreSQL / 接続用シークレット
│   └── app/                    # ECS / ALB / タスク定義
├── config/
│   └── config.yaml             # モデル・推論パラメータ
├── data/
│   └── raw/                    # NASA CMAPSS データ (train_FD001.txt 等)
├── docs/
│   ├── system_diagram.md       # Mermaid 構成図
│   ├── architecture.md         # アーキテクチャ解説 (v1)
│   ├── architecture_v2.md      # アーキテクチャ解説 (AWS 構成含む最新版)
│   ├── cloud_deployment.md     # AWS デプロイ手順
│   └── *.md                    # ECR / ECS / CloudWatch / Secrets Manager / Terraform 基礎メモ
├── notebooks/
│   └── EDA.ipynb               # 探索的データ分析
├── tests/
│   ├── api/                    # API テスト (TestClient)
│   └── services/               # Service 層ユニットテスト
├── .github/workflows/
│   ├── ci.yml                  # GitHub Actions CI (pytest)
│   └── deployment.yml          # ECR への push + ECS 再デプロイ
├── pytest.ini
└── requirements.txt
```

## Setup

Python dependencies:

```bash
pip install -r requirements.txt
```

WSL 上で実行する場合は、プロジェクトルートで仮想環境を作ると扱いやすいです。

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

環境変数は .env.example をコピーして設定します(API Key・DB 接続先など)。

```bash
cp .env.example .env
# API_KEY をデフォルトの dev-secret-key から変更することを推奨
```

## Training

学習済みモデルと scaler がない場合は、以下で作成します。

```bash
python -m src.train
```

出力:

```text
models/anomaly_api_model.pt
models/scaler.pkl
```

## Run API

Docker Compose:

```bash
docker compose -f docker/docker-compose.yml up --build
```

API:

```text
http://localhost:8080
```

Swagger UI:

```text
http://localhost:8080/docs
```

### その他のサービス(Docker Compose 起動時)
Prometheus: 
```text
http://localhost:9090
```

Grafana:
```text
http://localhost:3000
```

メトリクス: 
```text
http://localhost:8080/metrics
```

ヘルスチェック:

```bash
curl http://localhost:8080/
```

推論エンドポイントは X-API-Key ヘッダーが必須です(レート制限: 5 req/min)。

```bash
curl -X POST http://localhost:8080/predict \
  -H "X-API-Key: dev-secret-key" \
  -H "Content-Type: application/json" \
  -d @data/sample_request.json 
```

`seq_len=10` の場合、同じ `unit_number` のデータが最低 10 行必要です。
※ `data/sample_request.json` はリポジトリに含まれていません。
[scripts/test_api_manual.py](scripts/test_api_manual.py) のペイロードを参考に作成してください。

## Manual API Test

`scripts/test_api_manual.py` は正常系・欠損カラム・型不正・空 sequence の 4 パターンを
`http://localhost:8080/predict` に投げて応答を表示します
(現状 `X-API-Key` ヘッダーは付与しないため、認証エラー系の確認にも使えます)。
```bash
python scripts/test_api_manual.py
```

## Batch Prediction

入力CSV(リポジトリには含まれないため、事前に用意します):

```text
data/test_sequence.csv
```

実行:

```bash
python scripts/batch_predict.py
```

出力:

```text
results/batch_predictions.csv
```

## Logs

予測結果は `DATABASE_URL` で指定した DB の `prediction_logs` テーブルに永続化されます
(Docker/CI では PostgreSQL、ローカル既定では `sqlite:///./anomaly.db`)。

PostgreSQL の内容を確認する例(Docker Compose 起動中):

```bash
docker exec -it anomaly-db psql -U postgres -d anomaly_db -c "\d prediction_logs"
docker exec -it anomaly-db psql -U postgres -d anomaly_db -c "SELECT * FROM prediction_logs ORDER BY id DESC LIMIT 10;"
```

ダッシュボードからの可視化は上記「Dashboard」セクションを参照してください。

## Configuration

[config/config.yaml](config/config.yaml):

```yaml
model:
  version: "lstm_ae_v1"
  path: "models/anomaly_api_model.pt"
  scaler_path: "models/scaler.pkl"

inference:
  seq_len: 10
  rolling_window: 10
  threshold: 0.8
  consecutive_window: 5
```

実行時設定は [core/config.py](core/config.py)(pydantic-settings)が `.env` / 環境変数から読み込みます。
推論パラメータ(`seq_len` / `rolling_window` / `threshold` / `consecutive_window`)は
API リクエストボディでも上書きできます。


## Roadmap Status

- [x] LSTM AutoEncoder
- [x] FastAPI
- [x] PostgreSQL
- [x] Repository Pattern
- [x] Service Layer
- [x] Alembic
- [x] Docker
- [x] MLflow
- [x] Model Registry
- [x] Prometheus
- [x] Grafana
- [x] Streamlit
- [x] API Key
- [x] Rate Limit
- [x] Structured Logging
- [x] GitHub Actions
- [x] Terraform
- [x] ECS Deployment (ECS Fargate + ALB、Terraform 3層構成)


## Notes

このプロジェクトは実験・学習用途のドラフトです。モデル評価、閾値設計、データ分割、入力バリデーション、運用監視は継続改善の余地があります。
