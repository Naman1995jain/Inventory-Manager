#!/bin/bash

# Navigate to the scripts directory
cd "$(dirname "$0")"

# Print status message
echo "Setting up databases..."

# Run the script to create databases
echo "Creating databases..."
python create_databases.py

# Run the script to setup database
echo "Setting up database..."
python setup_database.py

echo "Setting up admin user..."

# Run the script to add the admin column to the users table
echo "Adding admin column to users table..."
python add_admin_column.py

# Run the script to create/update the admin user
echo "Creating/updating admin user..."
python create_admin_user.py

echo "Admin setup completed successfully!"