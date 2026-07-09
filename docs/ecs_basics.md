# ECS Basics

## Goal

Deploy the FastAPI container stored in Amazon ECR to Amazon ECS Fargate.

## Architecture

Local PC
    ↓
Docker Build
    ↓
Amazon ECR
    ↓
Amazon ECS Cluster
    ↓
Task Definition
    ↓
Service
    ↓
FastAPI Container

## Components

### Cluster

Container execution environment.

### Task Definition

Container specification including image, CPU, memory, ports, and environment variables.

### Service

Maintains the desired number of running tasks.

## Result

Successfully deployed the FastAPI container to Amazon ECS Fargate.

### Cluster
Container execution environment.

### Task Definition
Defines the container image, CPU, memory, networking, and runtime configuration.

### Service
Maintains the desired number of running tasks and automatically restarts failed tasks.

## Lessons Learned

- Amazon ECR stores Docker images.
- Amazon ECS Fargate runs containers without managing EC2 instances.
- A Task Definition acts as the deployment blueprint.
- A Service ensures the desired number of tasks remain running.