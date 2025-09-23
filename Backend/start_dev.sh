#!/bin/bash

# Development startup script for the Inventory Management API

echo "🚀 Starting Inventory Management API"
echo "===================================="

# Activate virtual environment
echo "📦 Activating virtual environment..."
source .venv/bin/activate

# Check if dependencies are installed
echo "🔍 Checking dependencies..."
if ! python -c "import fastapi" 2>/dev/null; then
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
fi

# Check database connection
echo "🗄️  Checking database connection..."
python -c "
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        result = connection.execute(text('SELECT 1'))
        print('✅ Database connection successful')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    print('Please ensure:')
    print('1. PostgreSQL is running')
    print('2. Database credentials in .env are correct')
    print('3. Database exists')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Database connection failed. Please check your configuration."
    exit 1
fi

# Setup database if needed
echo "🔧 Setting up database..."
python scripts/setup_database.py

# Start the application
echo ""
echo "🌟 Starting FastAPI application..."
echo "📖 API Documentation: http://localhost:8000/docs"
echo "🔄 API Redoc: http://localhost:8000/redoc"
echo "❤️  Health Check: http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
# Ensure logs directory exists so the logger can write immediately
mkdir -p logs

# Add project root to PYTHONPATH so app imports work when running via -m
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Use python -m uvicorn so our top-level `main` is imported and config runs
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000