# Secrets Manager

## Goal

Store sensitive configuration securely using AWS Secrets Manager.

## Secret

DATABASE_URL

## Architecture

Secrets Manager
      │
      ▼
ECS Task Definition
      │
      ▼
FastAPI

## Result

- DATABASE_URL was moved from plain environment variable to AWS Secrets Manager.
- ECS Task Definition was updated to reference the secret using Value From.
- FastAPI successfully connected to RDS PostgreSQL.
- /predict returned HTTP 200.
- prediction_logs increased from 1 row to 2 rows.