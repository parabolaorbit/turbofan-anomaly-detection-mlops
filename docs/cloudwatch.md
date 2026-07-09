# CloudWatch Monitoring

## Goal

Monitor FastAPI running on Amazon ECS using Amazon CloudWatch Logs.

## Architecture

ECS Fargate
    ↓
CloudWatch Logs
    ↓
Logs Insights

## Log Group

/ecs/turbofan-api-task

## Observed Logs

- Application startup complete
- Uvicorn running on port 8000
- POST /predict HTTP/1.1 200 OK
- Received prediction request
- prediction completed

## Logs Insights Queries

```sql
fields @timestamp, @message
| sort @timestamp desc
| limit 20