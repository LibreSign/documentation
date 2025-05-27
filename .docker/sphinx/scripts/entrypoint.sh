#!/bin/bash
set -e

export PIP_CACHE_DIR=/pipcache

echo "🔍 Checking for required dependencies..."

if ! python -c "import sphinx" &> /dev/null; then
    echo "📦 Dependencies not found. Installing..."

    echo "⬆️ Upgrading pip..."
    python -m pip install --upgrade pip

    echo "📥 Installing packages from /app/requirements.txt..."
    pip install -r "/app/requirements.txt"
else
    echo "✅ Dependencies already installed."
fi

echo "🛠️ Building documentation..."
sphinx-build -b html /app/main /app/_build/main
sphinx-build -b html /app/user /app/_build/user
sphinx-build -b html /app/admin /app/_build/admin
sphinx-build -b html /app/dev /app/_build/dev

sphinx-autobuild ./source ./_build/html
