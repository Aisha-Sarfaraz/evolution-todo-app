#!/usr/bin/env bash
# Phase IV: Build Docker images for todo-app
# Usage: ./phase-4/scripts/build.sh [--backend-only] [--frontend-only] [--tag TAG]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

TAG="${TAG:-latest}"
BUILD_BACKEND=true
BUILD_FRONTEND=true

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --backend-only) BUILD_FRONTEND=false; shift ;;
        --frontend-only) BUILD_BACKEND=false; shift ;;
        --tag) TAG="$2"; shift 2 ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

echo "=== Phase IV Docker Build ==="
echo "Tag: $TAG"
echo ""

if [ "$BUILD_BACKEND" = true ]; then
    echo "--- Building backend image: todo-backend:$TAG ---"
    docker build \
        -t "todo-backend:$TAG" \
        -f "$PROJECT_ROOT/phase-4/docker/backend.Dockerfile" \
        "$PROJECT_ROOT/phase-3/backend/"
    echo ""
    echo "Backend image size:"
    docker images "todo-backend:$TAG" --format "  {{.Repository}}:{{.Tag}} — {{.Size}}"
    echo ""
fi

if [ "$BUILD_FRONTEND" = true ]; then
    echo "--- Building frontend image: todo-frontend:$TAG ---"
    docker build \
        -t "todo-frontend:$TAG" \
        -f "$PROJECT_ROOT/phase-4/docker/frontend.Dockerfile" \
        "$PROJECT_ROOT/phase-3/frontend/"
    echo ""
    echo "Frontend image size:"
    docker images "todo-frontend:$TAG" --format "  {{.Repository}}:{{.Tag}} — {{.Size}}"
    echo ""
fi

echo "=== Build complete ==="
