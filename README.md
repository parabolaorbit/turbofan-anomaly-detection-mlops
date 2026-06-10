# Kaggle Turbofan Jet Engine Anomaly Detection
![Python](https://img.shields.io/badge/Python-3.11-blue)
![PyTorch](https://img.shields.io/badge/PyTorch-LSTM_AutoEncoder-red)
![FastAPI](https://img.shields.io/badge/FastAPI-REST_API-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED)

NASA turbofan engine degradationシミュレーション向けの
LSTM AutoEncoderによる異常検知システムです。

This project focuses not only on model training,
but also on operational AI system design including:

- FastAPI inference API
- prediction logging
- monitoring dashboard
- drift monitoring
- retraining decision support
- Docker Compose deployment

## Overview

- 入力: エンジンごとの時系列センサーデータ(unit_number / time_in_cycles / ope_setting1-3 / sensor_ms1-21)
- モデル: LSTM AutoEncoder
- 推論: 再構成誤差を anomaly score として算出
- API: FastAPI `/predict`, `/predict_batch`(ヘルスチェック: `GET /`)
- ログ: SQLAlchemy 経由で `prediction_logs` テーブルに保存
  (接続先は `DATABASE_URL`。デフォルトは `sqlite:///./anomaly.db`、Docker/CI では PostgreSQL を想定)
- 実行環境: Docker / Docker Compose / WSL

構成図は [system_diagram.md](docs/system_diagram.md) を参照してください。

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

## Dashboard

![Dashboard](docs/dashboard.png)

このダッシュボードは監視メトリクス、Severity、異常値スコアのトレンド、直近ログを可視化します。

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

- Python 3.11
- PyTorch
- pandas / NumPy / scikit-learn
- FastAPI / Pydantic / pydantic-settings
- SQLAlchemy
- PostgreSQL / SQLite
- Alembic
- Streamlit
- Docker / Docker Compose
- pytest / GitHub Actions


## Project Structure

```text
.
├── api/
│   ├── main.py                 # FastAPI アプリ・ルーター定義(lifespan でモデル読込)
│   └── api_model.py            # Pydantic リクエストモデル (SensorRecord / PredictRequest)
├── core/
│   └── config.py               # pydantic-settings による設定管理 (.env / 環境変数)
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
│   ├── prediction_logger.py    # (旧) JSONL ログ
│   └── sqlite_logger.py        # (旧) SQLite 直書きログ
├── scripts/
│   ├── dashboard.py            # Streamlit 監視ダッシュボード
│   ├── batch_predict.py        # CSV バッチ推論
│   ├── retraining_decision.py  # 再学習要否の自動判断
│   └── test_api_manual.py      # 手動 API テスト
├── alembic/                    # DB マイグレーション (alembic.ini はルート)
├── docker/
│   ├── docker-compose.yml      # anomaly-api + anomaly-db (PostgreSQL 16)
│   └── Dockerfile
├── config/
│   └── config.yaml             # モデル・推論パラメータ
├── data/
│   └── raw/                    # NASA CMAPSS データ (train_FD001.txt 等)
├── docs/
│   └── system_diagram.md       # Mermaid 構成図
├── notebooks/
│   └── EDA.ipynb               # 探索的データ分析
├── tests/
│   ├── api/                    # API テスト (TestClient)
│   └── services/               # Service 層ユニットテスト
├── .github/workflows/ci.yml    # GitHub Actions CI
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

ヘルスチェック:

```bash
curl http://localhost:8080/
```

`seq_len=10` の場合、同じ `unit_number` のデータが最低 10 行必要です。

## Manual API Test

```bash
python scripts/test_api_manual.py
```

## Batch Prediction

入力CSV:

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

## Dashboard

SQLite ログを Streamlit で確認します。

```bash
streamlit run scripts/dashboard.py
```

## Logs

Prediction logs:

```text
logs/predictions.jsonl
logs/predictions.db
```

Docker でホスト側にログを残すには、`logs` ディレクトリをコンテナへ volume mount します。

```yaml
volumes:
  - ./logs:/app/logs
  - ./models:/app/models
```

SQLite table:

```text
prediction_logs
```

確認例:

```bash
sqlite3 logs/predictions.db ".tables"
sqlite3 logs/predictions.db ".schema prediction_logs"
```

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

## Troubleshooting

### `Could not import module "main"`

FastAPI app は `api/main.py` にあるため、uvicorn の指定は以下にします。

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000
```




## Notes

このプロジェクトは実験・学習用途のドラフトです。モデル評価、閾値設計、データ分割、入力バリデーション、運用監視は継続改善の余地があります。
