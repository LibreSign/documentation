#!/bin/bash
set -e

export PIP_CACHE_DIR=/pipcache

echo "🔍 Checking for required dependencies..."

echo "⬆️ Upgrading pip..."
python -m pip install --upgrade pip

echo "📥 Installing packages from /app/docs/requirements.txt..."
pip install -r "/app/docs/requirements.txt"

echo "✅ Dependencies installed installed."

echo "🛠️ Building documentation..."

sphinx-autobuild --port 0 /app/docs/user /app/_build/user &
sphinx-autobuild --port 0 /app/docs/admin /app/_build/admin &
sphinx-autobuild --port 0 /app/docs/dev /app/_build/dev
