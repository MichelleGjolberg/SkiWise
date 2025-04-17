#!/bin/sh
kubectl apply -f backend/deployment/backend-secret.yaml
kubectl apply -f backend/deployment/backend-deployment.yaml
kubectl apply -f backend/deployment/backend-service.yaml

kubectl apply -f frontend/deployment/frontend-configmap.yaml
kubectl apply -f frontend/deployment/frontend-deployment.yaml
kubectl apply -f frontend/deployment/frontend-service.yaml