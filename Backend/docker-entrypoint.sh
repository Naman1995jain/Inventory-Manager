#!/bin/bash
set -e

echo "Starting Inventory Management Backend..."

# Function to wait for PostgreSQL to be available
wait_for_postgres() {
    echo " Waiting for PostgreSQL to be ready..."
    
    # Use environment variables or defaults
    DB_HOST=${DB_HOST:-localhost}
    DB_PORT=${DB_PORT:-5432}
    DB_USER=${DB_USER:-postgres}    
    DB_PASSWORD=${DB_PASSWORD:-}

    # Export PGPASSWORD so libpq-backed tools (pg_isready, psql) and Python DB libraries
    # using libpq will pick up the password automatically.
    if [ -n "$DB_PASSWORD" ]; then
        export PGPASSWORD="$DB_PASSWORD"
    else
        unset PGPASSWORD
    fi
    
    while ! pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" > /dev/null 2>&1; do
        echo " PostgreSQL is not ready yet... waiting 2 seconds"
        sleep 2
    done
    
    echo " PostgreSQL is ready!"
}

# Function to run database initialization
init_database() {
    echo "  Initializing database..."
    
    # Run database creation script
    echo " Running create_databases.py..."
    if python scripts/create_databases.py; then
        echo " Database creation completed"
    else
        echo " Database creation failed"
        exit 1
    fi
    
    # Run database setup script
    echo " Running setup_database.py..."
    if python scripts/setup_database.py; then
        echo " Database setup completed"
    else
        echo " Database setup failed"
        exit 1
    fi
    
    # Run add admin column script
    echo " Running add_admin_column.py..."
    if python scripts/add_admin_column.py; then
        echo " Admin column addition completed"
    else
        echo " Admin column addition failed"
        exit 1
    fi
    
    # Run create admin user script
    echo " Running create_admin_user.py..."
    if python scripts/create_admin_user.py; then
        echo " Admin user creation completed"
    else
        echo " Admin user creation failed"
        exit 1
    fi

    echo " Running scrape_and_store.py..."
    if python scripts/scrape_and_store.py; then
        echo " Scraping and storing completed"
    else
        echo " Scraping and storing failed"
        exit 1
    fi

    echo " Database initialization completed successfully!"
}

# Main execution
main() {
    # Wait for PostgreSQL to be ready
    wait_for_postgres
    
    # Initialize database
    init_database
    
    echo " Starting FastAPI application..."
    echo " Application will be available at: http://0.0.0.0:8000"
    echo " API documentation available at: http://0.0.0.0:8000/docs"
    
    # Execute the original command passed to the container
    exec "$@"
}

# Run main function
main "$@"