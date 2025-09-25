#!/bin/bash

# Backend Testing Script for Inventory Management System
# This script runs the complete test suite with different configurations

set -e  # Exit on any error

echo "🚀 Starting Backend Test Suite for Inventory Management System"
echo "================================================================"

# Change to backend directory
cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found. Creating one..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "📥 Installing/upgrading dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Set environment variables for testing
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
export DATABASE_URL="postgresql://test_user:test_password@localhost/inventory_test_db"
export TEST_DATABASE_URL="postgresql://test_user:test_password@localhost/inventory_test_db"
export SECRET_KEY="test_secret_key_for_testing_only"
export ALGORITHM="HS256"
export ACCESS_TOKEN_EXPIRE_MINUTES="30"
export DEBUG="False"

echo "🧪 Environment configured for testing"

# Function to run tests with different markers
run_tests() {
    local marker=$1
    local description=$2
    
    echo ""
    echo "🔍 Running $description..."
    echo "----------------------------------------"
    
    if [ "$marker" = "all" ]; then
        pytest -v --tb=short
    else
        pytest -v --tb=short -m "$marker"
    fi
    
    if [ $? -eq 0 ]; then
        echo "✅ $description passed!"
    else
        echo "❌ $description failed!"
        exit 1
    fi
}

# Function to run tests with coverage
run_coverage() {
    echo ""
    echo "📊 Running tests with coverage..."
    echo "----------------------------------------"
    
    pip install -q coverage pytest-cov
    
    pytest --cov=app --cov-report=html --cov-report=term-missing --cov-fail-under=80
    
    if [ $? -eq 0 ]; then
        echo "✅ Coverage tests passed!"
        echo "📄 Coverage report generated in htmlcov/index.html"
    else
        echo "❌ Coverage tests failed or coverage below 80%!"
        exit 1
    fi
}

# Parse command line arguments
case "${1:-all}" in
    "unit")
        run_tests "unit" "Unit Tests"
        ;;
    "integration")
        run_tests "integration" "Integration Tests"
        ;;
    "auth")
        run_tests "auth" "Authentication Tests"
        ;;
    "coverage")
        run_coverage
        ;;
    "fast")
        run_tests "unit" "Unit Tests (Fast)"
        ;;
    "all")
        echo "🔄 Running complete test suite..."
        run_tests "unit" "Unit Tests"
        run_tests "integration" "Integration Tests"
        run_coverage
        ;;
    "help"|"-h"|"--help")
        echo "Usage: $0 [test_type]"
        echo ""
        echo "Test types:"
        echo "  unit        - Run only unit tests"
        echo "  integration - Run only integration tests"
        echo "  auth        - Run only authentication tests"
        echo "  coverage    - Run tests with coverage report"
        echo "  fast        - Run only fast unit tests"
        echo "  all         - Run all tests (default)"
        echo "  help        - Show this help message"
        exit 0
        ;;
    *)
        echo "❌ Unknown test type: $1"
        echo "Use '$0 help' for available options"
        exit 1
        ;;
esac

echo ""
echo "🎉 All requested tests completed successfully!"
echo "================================================================"