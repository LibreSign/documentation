#!/bin/bash
set -e

echo "🔍 Checking for required dependencies..."

echo "⬆️ Upgrading pip..."
python -m pip install --upgrade pip

echo "📥 Installing packages from /app/requirements.txt..."
pip install -r "/app/requirements.txt"

echo "✅ Dependencies installed installed."

echo "🛠️ Building documentation..."

sphinx-autobuild --port 0 /app/user_manual /app/_build/user_manual &
sphinx-autobuild --port 0 /app/admin_manual /app/_build/admin_manual &
sphinx-autobuild --port 0 /app/developer_manual /app/_build/developer_manual &
sphinx-autobuild --port 0 /app/main /app/_build
