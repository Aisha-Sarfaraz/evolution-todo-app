#!/usr/bin/env bash
# Phase IV: Deploy todo-app to Minikube via Helm
# Usage: ./phase-4/scripts/deploy.sh [--upgrade] [--dev]
#
# Required env vars (or pass via --set):
#   DATABASE_URL, OPENROUTER_API_KEY, BETTER_AUTH_SECRET, VAPID_PRIVATE_KEY, VAPID_PUBLIC_KEY

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CHART_DIR="$PROJECT_ROOT/phase-4/helm/todo-app"
RELEASE_NAME="todo-app"
NAMESPACE="todo-app"

UPGRADE=false
DEV_VALUES=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --upgrade) UPGRADE=true; shift ;;
        --dev) DEV_VALUES=true; shift ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

echo "=== Phase IV Kubernetes Deployment ==="

# Build helm command
HELM_CMD="helm"
if [ "$UPGRADE" = true ]; then
    HELM_CMD="$HELM_CMD upgrade --atomic $RELEASE_NAME $CHART_DIR"
else
    HELM_CMD="$HELM_CMD install $RELEASE_NAME $CHART_DIR"
fi

# Add dev values overlay
if [ "$DEV_VALUES" = true ]; then
    HELM_CMD="$HELM_CMD -f $CHART_DIR/values-dev.yaml"
fi

# Inject secrets from environment variables
HELM_CMD="$HELM_CMD \
    --set secrets.databaseUrl=\"${DATABASE_URL:-}\" \
    --set secrets.openrouterApiKey=\"${OPENROUTER_API_KEY:-}\" \
    --set secrets.betterAuthSecret=\"${BETTER_AUTH_SECRET:-}\" \
    --set secrets.vapidPrivateKey=\"${VAPID_PRIVATE_KEY:-}\" \
    --set secrets.vapidPublicKey=\"${VAPID_PUBLIC_KEY:-}\""

echo "Running: $HELM_CMD"
eval "$HELM_CMD"

echo ""
echo "--- Waiting for pods to be ready ---"
kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance=$RELEASE_NAME -n $NAMESPACE --timeout=60s 2>/dev/null || \
    echo "Warning: Pods not ready within 60s. Check: kubectl get pods -n $NAMESPACE"

echo ""
echo "--- Pod Status ---"
kubectl get pods -n $NAMESPACE

echo ""
echo "--- Service Status ---"
kubectl get svc -n $NAMESPACE

echo ""
echo "=== Deployment complete ==="
echo "Run 'minikube tunnel' in a separate terminal to access the frontend LoadBalancer."
