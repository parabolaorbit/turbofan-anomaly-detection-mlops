# Cloud Deployment Plan

## Current Architecture

- FastAPI
- PostgreSQL
- MLflow
- Prometheus
- Grafana
- Streamlit

## Target Cloud

AWS ECS

## Container Platform
- Amazon ECS Fargate

## Mapping

FastAPI -> ECS Fargate
PostgreSQL -> Amazon RDS PostgreSQL
MLflow -> ECS Fargate
Scheduler -> Amazon EventBridge
Grafana -> Amazon Managed Grafana
Prometheus -> Amazon Managed Service for Prometheus
Scheduler -> Amazon EventBridge
Docker Image -> Amazon ECR
Streamlit -> ECS Fargate

## Deployment Flow

Developer 
↓
GitHub
↓
GitHub Actions
↓
Amazon ECR
↓
Amazon ECS Fargate
↓
RDS PostgreSQL

## Future Enhancements
Terraform IaC
Blue/Green Deployment
ECS Auto Scaling
Secrets Manager
CloudWatch Logging
CI/CD Pipeline
Multi Environment (dev/stg/prod)

## Architecture Goals
Container-based deployment
Managed database
Managed monitoring
Automated retraining
Scalable AI inference platform