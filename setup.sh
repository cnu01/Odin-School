#!/bin/bash
set -euo pipefail

echo "🚀 Odin School EdTech Solutions Backend"
echo "======================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment for this script's duration
if [ -f "venv/bin/activate" ]; then
    echo "🛠️  Using virtual environment (script-local)..."
    # shellcheck disable=SC1091
    source venv/bin/activate
else
    echo "❌ venv activation script missing at venv/bin/activate" >&2
    exit 1
fi

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Ensure a .env file exists
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "⚙️  Creating .env file from template..."
        cp .env.example .env
        echo "Please edit .env file with your settings before running the app"
    else
        echo "⚠️  No .env or .env.example found. Create a .env before running the app." >&2
    fi
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next: activate the venv in your current shell before running the app:"
echo "  source venv/bin/activate"
echo ""
echo "� Commands:"
echo "  fastapi dev main.py          # Start development server"
echo "  uvicorn main:app --reload    # Alternative"
echo ""
echo "📖 API Docs: http://localhost:8000/docs"
