#!/usr/bin/env bash
# Phase IV: Tear down todo-app from Minikube
# Usage: ./phase-4/scripts/teardown.sh [--delete-namespace]

set -euo pipefail

RELEASE_NAME="todo-app"
NAMESPACE="todo-app"
DELETE_NS=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --delete-namespace) DELETE_NS=true; shift ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

echo "=== Phase IV Teardown ==="

echo "Uninstalling Helm release: $RELEASE_NAME"
helm uninstall "$RELEASE_NAME" 2>/dev/null && echo "Release uninstalled." || echo "Release not found (already removed?)."

if [ "$DELETE_NS" = true ]; then
    echo "Deleting namespace: $NAMESPACE"
    kubectl delete namespace "$NAMESPACE" 2>/dev/null && echo "Namespace deleted." || echo "Namespace not found."
fi

echo ""
echo "=== Teardown complete ==="
