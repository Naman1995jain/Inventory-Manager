#!/bin/bash

# Test runner script for the Inventory Management API

echo "🧪 Running Inventory Management API Tests"
echo "=========================================="

# Activate virtual environment
echo "📦 Activating virtual environment..."
source .venv/bin/activate

# Check if pytest is available
if ! command -v pytest &> /dev/null; then
    echo "❌ pytest not found. Installing..."
    pip install pytest pytest-asyncio httpx
fi

echo ""
echo "🔍 Running tests..."
echo ""

# Add the current directory to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Ensure logs directory exists so logging can write during tests
mkdir -p logs

# Run tests with coverage if available
if command -v pytest-cov &> /dev/null; then
    pytest --cov=app --cov-report=term-missing --cov-report=html -v
else
    pytest -v
fi

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ All tests passed!"
    echo ""
    echo "📊 Coverage report generated in htmlcov/index.html"
else
    echo ""
    echo "❌ Some tests failed. Please check the output above."
    exit 1
fi