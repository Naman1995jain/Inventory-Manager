#!/bin/bash

# Pull latest images
docker pull ${DOCKER_USERNAME}/inventory-backend:latest
docker pull ${DOCKER_USERNAME}/inventory-frontend:latest

# Stop and remove existing containers
docker-compose down

# Start new containers
docker-compose up -d

# Clean up old images
docker image prune -f