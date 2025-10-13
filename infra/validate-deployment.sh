#!/bin/bash
set -e

# Validation script for Azure deployment
# This script tests that all deployed resources are working correctly

echo "🔍 Validating Azure deployment..."

# Load environment variables from .env file
if [ -f "../.env" ]; then
    echo "Loading environment variables from .env file..."
    export $(grep -v '^#' ../.env | xargs)
else
    echo "❌ Error: .env file not found. Please run deploy.sh first."
    exit 1
fi

echo ""
echo "📋 Testing Azure Resources..."

# Test 1: PostgreSQL Connection
echo "🔗 Testing PostgreSQL connection..."
if PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_DB_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT version();" > /dev/null 2>&1; then
    echo "✅ PostgreSQL connection successful"
    
    # Test database schema
    TABLE_COUNT=$(PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_DB_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'retail';" | tr -d ' ')
    echo "   └── Found $TABLE_COUNT tables in retail schema"
    
    # Test sample data
    CUSTOMER_COUNT=$(PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_DB_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -t -c "SELECT COUNT(*) FROM retail.customers;" | tr -d ' ')
    echo "   └── Found $CUSTOMER_COUNT customers in database"
    
    # Test pgvector extension
    if PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_DB_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT * FROM pg_extension WHERE extname = 'vector';" | grep -q "vector"; then
        echo "   └── pgvector extension is enabled"
    else
        echo "   └── ⚠️  pgvector extension not found"
    fi
else
    echo "❌ PostgreSQL connection failed"
fi

# Test 2: Azure OpenAI Connection
echo ""
echo "🤖 Testing Azure OpenAI connection..."
if [ -n "$AZURE_CLIENT_ID" ] && [ -n "$AZURE_CLIENT_SECRET" ] && [ -n "$AZURE_TENANT_ID" ] && [ -n "$AZURE_OPENAI_ENDPOINT" ]; then
    echo "✅ Azure OpenAI credentials are configured"
    echo "   └── Endpoint: $AZURE_OPENAI_ENDPOINT"
    echo "   └── Embedding Model: $EMBEDDING_MODEL_DEPLOYMENT_NAME"
    if [ -n "$GPT_MODEL_DEPLOYMENT_NAME" ]; then
        echo "   └── GPT Model: $GPT_MODEL_DEPLOYMENT_NAME"
    else
        echo "   └── GPT Model: Not deployed"
    fi
else
    echo "❌ Azure OpenAI credentials are missing"
fi

# Test 3: Application Insights
echo ""
echo "📊 Testing Application Insights..."
if [ -n "$APPLICATIONINSIGHTS_CONNECTION_STRING" ]; then
    echo "✅ Application Insights connection string is configured"
else
    echo "❌ Application Insights connection string is missing"
fi

# Test 4: Test MCP Server Dependencies
echo ""
echo "🔧 Testing MCP server dependencies..."

# Check if required Python packages are available
python3 -c "import psycopg2" 2>/dev/null && echo "✅ psycopg2 (PostgreSQL driver) available" || echo "❌ psycopg2 not available"
python3 -c "import azure.identity" 2>/dev/null && echo "✅ azure-identity available" || echo "❌ azure-identity not available"
python3 -c "import openai" 2>/dev/null && echo "✅ openai package available" || echo "❌ openai package not available"

# Test 5: Sample MCP Query
echo ""
echo "🧪 Testing sample database query..."
if PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_DB_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "
SELECT 
    s.store_name,
    COUNT(o.order_id) as total_orders,
    ROUND(SUM(oi.quantity * oi.unit_price)::numeric, 2) as total_revenue
FROM retail.stores s
LEFT JOIN retail.orders o ON s.store_id = o.store_id
LEFT JOIN retail.order_items oi ON o.order_id = oi.order_id
GROUP BY s.store_id, s.store_name
ORDER BY total_revenue DESC
LIMIT 3;
" > /dev/null 2>&1; then
    echo "✅ Sample sales analytics query successful"
else
    echo "❌ Sample sales analytics query failed"
fi

echo ""
echo "🎉 Validation complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Open the project in VS Code: code ."
echo "2. Use Ctrl+Shift+P -> 'Tasks: Run Task' -> 'Start Supplier and Finance MCP Servers'"
echo "3. Configure MCP in your AI assistant (Claude, etc.) using the servers in .vscode/mcp.json"
echo ""
echo "📚 For more information, see the README.md file."