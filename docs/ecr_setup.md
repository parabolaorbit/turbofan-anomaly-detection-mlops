# ECR Setup

## Goal
Docker ImageをAWS ECRへ登録する

## Architecture
Local PC -> Docker Build -> Docker Image -> AWS ECR

## Steps

### Create Repository

aws ecr create-repository --repository-name turbofan-anomaly-api

### Docker Build
docker build -t turbofan-anomaly-api -f docker/Dockerfile .

### Docker Push
docker tag turbofan-anomaly-api:latest 097853039113.dkr.ecr.ap-northeast-1.amazonaws.com/turbofan-anomaly-api:latest
docker push 097853039113.dkr.ecr.ap-northeast-1.amazonaws.com/turbofan-anomaly-api:latest

## Result
turbofan-anomaly-api:latestをECRへ登録完了

----------------------------------------------------------------
# ECR Setup

## Goal

FastAPIアプリケーションをAWS ECSへデプロイするため、
Docker ImageをAmazon ECRへ登録する。

---

## Architecture

Local PC
    ↓
Docker Build
    ↓
Docker Image
    ↓
Amazon ECR
    ↓
Amazon ECS (Day62)

---

## Prerequisites

- AWS CLI configured
- Docker installed
- ECR repository created

---

## Create Repository

aws ecr create-repository \
  --repository-name turbofan-anomaly-api

---

## Build Docker Image

docker build \
  -t turbofan-anomaly-api \
  -f docker/Dockerfile .

---

## Login to ECR

aws ecr get-login-password \
  --region ap-northeast-1 \
| docker login \
  --username AWS \
  --password-stdin \
  097853039113.dkr.ecr.ap-northeast-1.amazonaws.com

---

## Push Image

docker tag turbofan-anomaly-api:latest \
097853039113.dkr.ecr.ap-northeast-1.amazonaws.com/turbofan-anomaly-api:latest

docker push \
097853039113.dkr.ecr.ap-northeast-1.amazonaws.com/turbofan-anomaly-api:latest

---

## Result

Successfully pushed:

097853039113.dkr.ecr.ap-northeast-1.amazonaws.com/turbofan-anomaly-api:latest

---

## Lessons Learned

- ECR is AWS managed container registry.
- ECS pulls Docker images from ECR.
- InvalidClientTokenId indicates AWS credential issues.
- Docker push requires valid ECR authentication.

## Troubleshooting

### InvalidClientTokenId

Cause:
Expired or invalid AWS CLI credentials.

Solution:
Reconfigure AWS CLI using `aws configure`.

---

### Large Docker Image

Cause:
`torch` was installed twice (Dockerfile + requirements.txt).

Solution:
Remove `torch` from `requirements.txt` and install the CPU version only in the Dockerfile.

Result:
Docker image size reduced from 4490 MB to 555 MB.