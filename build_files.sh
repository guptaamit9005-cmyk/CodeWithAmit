#!/bin/bash
set -e

echo "=== Installing dependencies for build ==="
if command -v python3 &> /dev/null; then
    PY_BIN="python3"
else
    PY_BIN="python"
fi

if command -v uv &> /dev/null; then
    echo "Using uv to install dependencies..."
    uv pip install -r requirements.txt --system
else
    echo "Using pip to install dependencies..."
    $PY_BIN -m pip install -r requirements.txt --break-system-packages 2>/dev/null || $PY_BIN -m pip install -r requirements.txt
fi

echo "=== Collecting static files ==="
$PY_BIN manage.py collectstatic --no-input --clear

if [ -n "$DATABASE_URL" ]; then
    echo "=== Running database migrations ==="
    $PY_BIN manage.py migrate --no-input || true
fi

echo "=== Build finished successfully ==="
