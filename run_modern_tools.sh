#!/bin/bash

# Modern Python Development Tools Script
# Run Ruff linting and PyTest testing

echo "🚀 Running Modern Python Development Tools"
echo "=========================================="

cd "$(dirname "$0")/apps/backend"

echo
echo "📋 Installing/Upgrading development dependencies..."
pip install -q ruff pytest pytest-django pytest-cov

echo
echo "🔍 Running Ruff linter..."
echo "------------------------"
ruff check . --fix || echo "⚠️  Linting issues found (some may be auto-fixed)"

echo
echo "📝 Running Ruff formatter..."  
echo "--------------------------"
ruff format .

echo
echo "🧪 Running PyTest with coverage..."
echo "--------------------------------"
# Use SQLite for tests to avoid PostgreSQL extension issues
export DJANGO_SETTINGS_MODULE="config.settings"
pytest test_modern.py -v --tb=short --cov=core --cov-report=term-missing

echo
echo "✅ Modern tooling complete!"
echo
echo "💡 Tips:"
echo "  - Run 'ruff check .' to lint without fixing"
echo "  - Run 'ruff format .' to format code" 
echo "  - Run 'pytest -v' for verbose test output"
echo "  - Run 'pytest --cov=core' for coverage report"