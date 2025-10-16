#!/bin/bash
set -e

# PostgreSQL Database Initialization Script for Azure
# This script initializes the Azure PostgreSQL database with the Zava retail data

echo "Initializing Azure PostgreSQL database..."

# Load environment variables from .env file
if [ -f "../.env" ]; then
    echo "Loading environment variables from .env file..."
    export $(grep -v '^#' ../.env | xargs)
else
    echo "Error: .env file not found. Please run deploy.sh first."
    exit 1
fi

# Check required environment variables
if [ -z "$POSTGRES_DB_HOST" ] || [ -z "$POSTGRES_USER" ] || [ -z "$POSTGRES_PASSWORD" ] || [ -z "$POSTGRES_DB" ]; then
    echo "Error: Missing required PostgreSQL environment variables."
    echo "Required variables: POSTGRES_DB_HOST, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB"
    exit 1
fi

echo "Connecting to PostgreSQL server: $POSTGRES_DB_HOST"

# Verify postgresql-client is available (should be installed in container)
if ! command -v psql &> /dev/null; then
    echo "❌ Error: postgresql-client is not available."
    echo "This should be installed in the dev container. Please rebuild the container."
    exit 1
fi
echo "✅ PostgreSQL client is available."

# Test connection with retry logic
echo "Testing database connection..."
MAX_RETRIES=5
RETRY=1

while [ $RETRY -le $MAX_RETRIES ]; do
    echo "Connection attempt $RETRY/$MAX_RETRIES..."
    
    if PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_DB_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT version();" > /dev/null 2>&1; then
        echo "✅ Connection successful!"
        break
    else
        if [ $RETRY -eq $MAX_RETRIES ]; then
            echo "❌ Error: Failed to connect to PostgreSQL database after $MAX_RETRIES attempts."
            echo ""
            echo "Common causes:"
            echo "  - Firewall rules still propagating (wait 10-15 minutes)"
            echo "  - Network connectivity issues"
            echo "  - Incorrect credentials"
            echo ""
            echo "Connection details:"
            echo "  Host: $POSTGRES_DB_HOST"
            echo "  Database: $POSTGRES_DB"
            echo "  User: $POSTGRES_USER"
            echo ""
            echo "Try running this script again in a few minutes."
            exit 1
        else
            echo "Connection failed, waiting 30 seconds before retry..."
            sleep 30
        fi
    fi
    
    RETRY=$((RETRY + 1))
done

echo "✅ Database connection successful."

# Check if database has already been initialized
echo "Checking if database has already been initialized..."
if PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_DB_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT 1 FROM information_schema.tables WHERE table_name = 'customers' AND table_schema = 'retail';" 2>/dev/null | grep -q "1"; then
    echo "✅ Database appears to already be initialized. Skipping initialization."
    exit 0
fi

# Enable required extensions
echo "Enabling required PostgreSQL extensions..."
PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_DB_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "CREATE EXTENSION IF NOT EXISTS vector;"
PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_DB_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "CREATE EXTENSION IF NOT EXISTS plpgsql;"

# Create store_manager user if it doesn't exist
echo "Creating store_manager user..."
STORE_MANAGER_PASSWORD="StoreManager123"

if PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_DB_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT 1 FROM pg_roles WHERE rolname='store_manager';" 2>/dev/null | grep -q "1"; then
    echo "✅ User 'store_manager' already exists"
else
    echo "Creating 'store_manager' user..."
    PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_DB_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "CREATE USER store_manager WITH PASSWORD '${STORE_MANAGER_PASSWORD}';" || {
        echo "Warning: Failed to create store_manager user"
    }
    echo "✅ User 'store_manager' created successfully"
fi

# Grant privileges to store_manager
echo "Granting privileges to 'store_manager'..."
PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_DB_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "GRANT ALL PRIVILEGES ON DATABASE \"$POSTGRES_DB\" TO store_manager;" || {
    echo "Warning: Failed to grant database privileges to store_manager"
}

# Restore the database from backup
BACKUP_FILE="../data/github_retail_with_supplier_2025_10_16.backup"

if [ -f "$BACKUP_FILE" ]; then
    echo "Found backup file: $BACKUP_FILE"
    echo "Restoring database contents..."
    
    # Restore the database
    PGPASSWORD="$POSTGRES_PASSWORD" pg_restore -h "$POSTGRES_DB_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v "$BACKUP_FILE" || {
        echo "Warning: Some restoration errors occurred. This may be normal for certain backup types."
        echo "Continuing with initialization..."
    }
    
    # Update privileges after restore
    echo "Updating privileges after restore..."
    PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_DB_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO store_manager;" || true
    PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_DB_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO store_manager;" || true
    PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_DB_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO store_manager;" || true
    PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_DB_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA retail TO store_manager;" || true
    PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_DB_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA retail TO store_manager;" || true
    
    echo "✅ Database restoration completed."
else
    echo "❌ Error: Backup file not found at $BACKUP_FILE"
    echo "Please ensure the backup file exists before running this script."
    exit 1
fi

# Verify the restoration
echo "Verifying database restoration..."
TABLE_COUNT=$(PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_DB_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'retail';")
echo "Found $TABLE_COUNT tables in the retail schema."

if [ "$TABLE_COUNT" -gt 0 ]; then
    echo "✅ Database initialization completed successfully!"
else
    echo "❌ Warning: No tables found in retail schema. Initialization may have failed."
fi

echo ""
echo "🎉 Azure PostgreSQL database initialization complete!"
echo "📋 Connection Details:"
echo "  Host: $POSTGRES_DB_HOST"
echo "  Database: $POSTGRES_DB"
echo "  User: $POSTGRES_USER"
echo "  Application User: store_manager"
echo ""
echo "You can now use the MCP servers with the Azure PostgreSQL database."
echo ""
echo "📚 Troubleshooting:"
echo "  - If database connection fails, ensure the PostgreSQL server is fully ready"
echo "  - Run '../infra/validate-deployment.sh' to check all components"
echo "  - Check the .env file for correct connection parameters"