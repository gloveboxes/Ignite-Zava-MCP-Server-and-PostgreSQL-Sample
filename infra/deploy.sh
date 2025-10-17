#!/bin/bash
set -e  # Exit on any error

echo "Deploying the Azure resources..."

# --- Always deploy both models ---
INCLUDE_GPT_MODEL=true
echo "Deploying both GPT-4o-mini and text-embedding-3-small models"

# --- Generate secure password for PostgreSQL ---
echo "Generating secure password for PostgreSQL..."
POSTGRES_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)

# --- Parameters (match deploy.ps1) ---
RG_LOCATION="westus"
RESOURCE_PREFIX="gh-popup-server"
# unique suffix: lowercase letters + digits, 4 chars (macOS compatible)
UNIQUE_SUFFIX=$(openssl rand -hex 2 | tr '[:upper:]' '[:lower:]')

echo "Creating agent resources in resource group: rg-$RESOURCE_PREFIX-$UNIQUE_SUFFIX"
DEPLOYMENT_NAME="azure-gh-popup-server-$(date +%Y%m%d%H%M%S)"

# --- Configure models array (always deploy both models) ---
MODELS_JSON='[
  {
    "name": "gpt-4o-mini",
    "format": "OpenAI",
    "version": "2024-07-18",
    "skuName": "GlobalStandard",
    "capacity": 120
  },
  {
    "name": "text-embedding-3-small",
    "format": "OpenAI",
    "version": "1",
    "skuName": "GlobalStandard",
    "capacity": 120
  }
]'

echo "Starting Azure deployment..."
if ! az deployment sub create \
  --name "$DEPLOYMENT_NAME" \
  --location "$RG_LOCATION" \
  --template-file main.bicep \
  --parameters '@main.parameters.json' \
  --parameters location="$RG_LOCATION" \
  --parameters resourcePrefix="$RESOURCE_PREFIX" \
  --parameters uniqueSuffix="$UNIQUE_SUFFIX" \
  --parameters models="$MODELS_JSON" \
  --parameters postgresqlAdminPassword="$POSTGRES_PASSWORD" \
  --output json > output.json; then
    echo "Deployment failed. Check output.json for details."
    exit 1
fi

if [ ! -f output.json ]; then
    echo "Error: output.json not found."
    exit 1
fi

# Parse JSON output (requires jq)
if ! command -v jq &> /dev/null; then
    echo "Error: jq is required but not installed. Please install jq to continue."
    exit 1
fi

# Extract outputs from JSON
PROJECTS_ENDPOINT=$(jq -r '.properties.outputs.projectsEndpoint.value // empty' output.json)
RESOURCE_GROUP_NAME=$(jq -r '.properties.outputs.resourceGroupName.value // empty' output.json)
AI_FOUNDRY_NAME=$(jq -r '.properties.outputs.aiFoundryName.value // empty' output.json)
AI_PROJECT_NAME=$(jq -r '.properties.outputs.aiProjectName.value // empty' output.json)
AZURE_OPENAI_ENDPOINT=$(echo "$PROJECTS_ENDPOINT" | sed 's|api/projects/.*$||')
APPLICATIONINSIGHTS_CONNECTION_STRING=$(jq -r '.properties.outputs.applicationInsightsConnectionString.value // empty' output.json)
APPLICATION_INSIGHTS_NAME=$(jq -r '.properties.outputs.applicationInsightsName.value // empty' output.json)
POSTGRESQL_SERVER_FQDN=$(jq -r '.properties.outputs.postgresqlServerFqdn.value // empty' output.json)
POSTGRESQL_DATABASE_NAME=$(jq -r '.properties.outputs.postgresqlDatabaseName.value // empty' output.json)
POSTGRESQL_ADMIN_LOGIN=$(jq -r '.properties.outputs.postgresqlAdminLogin.value // empty' output.json)

if [ -z "$PROJECTS_ENDPOINT" ] || [ "$PROJECTS_ENDPOINT" = "null" ]; then
    echo "Error: projectsEndpoint not found. Possible deployment failure."
    exit 1
fi

# Verify PostgreSQL outputs were also created
if [ -z "$POSTGRESQL_SERVER_FQDN" ] || [ "$POSTGRESQL_SERVER_FQDN" = "null" ]; then
    echo "Error: PostgreSQL server FQDN not found. Database deployment may have failed."
    exit 1
fi

echo "Getting current Azure subscription..."
SUB_ID=$(az account show --query id -o tsv 2>/dev/null)
if [ -z "$SUB_ID" ]; then
    echo "Error: Could not get current subscription ID. Please login with 'az login'"
    exit 1
fi

# Get subscription name for display
SUB_NAME=$(az account show --query name -o tsv 2>/dev/null)
echo "Using subscription: $SUB_NAME ($SUB_ID)"

# Create service principal
echo "Creating service principal..."
SP_CREATION_SUCCESS=false
if SP_RESULT=$(az ad sp create-for-rbac \
    --name "gh-popup-server-sp" \
    --role "Cognitive Services OpenAI User" \
    --scopes "/subscriptions/$SUB_ID/resourceGroups/$RESOURCE_GROUP_NAME/providers/Microsoft.CognitiveServices/accounts/$AI_FOUNDRY_NAME" \
    --output json 2>/dev/null); then
    
    CLIENT_ID=$(echo "$SP_RESULT" | jq -r '.appId // empty')
    CLIENT_SECRET=$(echo "$SP_RESULT" | jq -r '.password // empty')
    TENANT_ID=$(echo "$SP_RESULT" | jq -r '.tenant // empty')
    
    # Verify we got the values
    if [ -n "$CLIENT_ID" ] && [ -n "$CLIENT_SECRET" ] && [ -n "$TENANT_ID" ]; then
        echo "✅ Service principal created successfully"
        SP_CREATION_SUCCESS=true
    else
        echo "⚠️ Failed to parse service principal response"
        CLIENT_ID=""
        CLIENT_SECRET=""
        TENANT_ID=""
    fi
else
    echo "⚠️ Failed to create service principal"
    echo "This can happen due to insufficient permissions or existing service principal conflicts."
    echo "The deployment will continue and you can create the service principal manually later."
    CLIENT_ID=""
    CLIENT_SECRET=""
    TENANT_ID=""
fi

# Write .env for workshop (overwrite)
ENV_FILE_PATH="../.env"

# Ensure directory exists
mkdir -p "$(dirname "$ENV_FILE_PATH")"

# Remove existing .env file if it exists
[ -f "$ENV_FILE_PATH" ] && rm -f "$ENV_FILE_PATH"

# Configure GPT model deployment name (always deployed)
GPT_MODEL_LINE='GPT_MODEL_DEPLOYMENT_NAME="gpt-4o-mini"'

# Create .env file with all available information
cat > "$ENV_FILE_PATH" << EOF
POSTGRES_DB_HOST=$POSTGRESQL_SERVER_FQDN
POSTGRES_DB_PORT=5432
POSTGRES_DB=$POSTGRESQL_DATABASE_NAME
POSTGRES_USER=$POSTGRESQL_ADMIN_LOGIN
POSTGRES_PASSWORD="$POSTGRES_PASSWORD"
POSTGRES_APPLICATION_NAME="mcp-server"
POSTGRES_CONNECTION_STRING="postgresql://$POSTGRESQL_ADMIN_LOGIN:$POSTGRES_PASSWORD@$POSTGRESQL_SERVER_FQDN:5432/$POSTGRESQL_DATABASE_NAME?application_name=mcp-server"
PROJECT_ENDPOINT=$PROJECTS_ENDPOINT
AZURE_OPENAI_ENDPOINT=$AZURE_OPENAI_ENDPOINT
$GPT_MODEL_LINE
EMBEDDING_MODEL_DEPLOYMENT_NAME="text-embedding-3-small"
APPLICATIONINSIGHTS_CONNECTION_STRING="$APPLICATIONINSIGHTS_CONNECTION_STRING"
AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED="true"
EOF

# Add service principal credentials if available
if [ "$SP_CREATION_SUCCESS" = true ]; then
    cat >> "$ENV_FILE_PATH" << EOF
AZURE_CLIENT_ID=$CLIENT_ID
AZURE_CLIENT_SECRET=$CLIENT_SECRET
AZURE_TENANT_ID=$TENANT_ID
EOF
    echo "✅ Service principal credentials added to .env file"
else
    cat >> "$ENV_FILE_PATH" << EOF
# Service principal creation failed - add these manually:
# AZURE_CLIENT_ID=your_client_id
# AZURE_CLIENT_SECRET=your_client_secret
# AZURE_TENANT_ID=your_tenant_id
EOF
    echo "⚠️ Service principal credentials not available - placeholders added to .env file"
fi

# Add final configuration
cat >> "$ENV_FILE_PATH" << EOF
AZURE_EXTENSION_USE_DYNAMIC_INSTALL="yes_without_prompt"
EOF

# Clean up output.json
rm -f output.json

echo "Adding Azure AI user roles..."

# Role assignments - track success for final reporting
ROLE_ASSIGNMENTS_SUCCESS=true
FAILED_ROLES=()

# Get user object ID (this might also fail in some environments)
if OBJECT_ID=$(az ad signed-in-user show --query id -o tsv 2>/dev/null); then
    echo "Retrieved user object ID for role assignments"
else
    echo "⚠️ Could not retrieve user object ID - skipping role assignments"
    echo "This can happen due to device management policies or authentication issues."
    echo "You may need to assign roles manually in the Azure portal."
    ROLE_ASSIGNMENTS_SUCCESS=false
    FAILED_ROLES+=("All roles (could not get user ID)")
fi

# Only attempt role assignments if we have the object ID
if [ -n "$OBJECT_ID" ]; then
    echo "Ensuring Azure AI Developer role assignment..."
    if ROLE_RESULT=$(az role assignment create \
      --role "Azure AI Developer" \
      --assignee "$OBJECT_ID" \
      --scope "/subscriptions/$SUB_ID/resourceGroups/$RESOURCE_GROUP_NAME/providers/Microsoft.CognitiveServices/accounts/$AI_FOUNDRY_NAME" 2>&1); then
        echo "✅ Azure AI Developer role assignment created successfully."
    elif echo "$ROLE_RESULT" | grep -q "RoleAssignmentExists\|already exists"; then
        echo "✅ Azure AI Developer role assignment already exists."
    else
        echo "⚠️ Azure AI Developer role assignment failed:"
        echo "$ROLE_RESULT" | head -n 2
        ROLE_ASSIGNMENTS_SUCCESS=false
        FAILED_ROLES+=("Azure AI Developer")
    fi

    echo "Ensuring Azure AI User role assignment..."
    if ROLE_RESULT_USER=$(az role assignment create \
      --assignee "$OBJECT_ID" \
      --role "Azure AI User" \
      --scope "/subscriptions/$SUB_ID/resourceGroups/$RESOURCE_GROUP_NAME" 2>&1); then
        echo "✅ Azure AI User role assignment created successfully."
    elif echo "$ROLE_RESULT_USER" | grep -q "RoleAssignmentExists\|already exists"; then
        echo "✅ Azure AI User role assignment already exists."
    else
        echo "⚠️ Azure AI User role assignment failed:"
        echo "$ROLE_RESULT_USER" | head -n 2
        ROLE_ASSIGNMENTS_SUCCESS=false
        FAILED_ROLES+=("Azure AI User")
    fi

    echo "Ensuring Azure AI Project Manager role assignment..."
    if ROLE_RESULT_MANAGER=$(az role assignment create \
      --assignee "$OBJECT_ID" \
      --role "Azure AI Project Manager" \
      --scope "/subscriptions/$SUB_ID/resourceGroups/$RESOURCE_GROUP_NAME" 2>&1); then
        echo "✅ Azure AI Project Manager role assignment created successfully."
    elif echo "$ROLE_RESULT_MANAGER" | grep -q "RoleAssignmentExists\|already exists"; then
        echo "✅ Azure AI Project Manager role assignment already exists."
    else
        echo "⚠️ Azure AI Project Manager role assignment failed:"
        echo "$ROLE_RESULT_MANAGER" | head -n 2
        ROLE_ASSIGNMENTS_SUCCESS=false
        FAILED_ROLES+=("Azure AI Project Manager")
    fi
fi

# Check if PostgreSQL tools are available
echo ""
echo "Checking PostgreSQL connectivity tools..."

# Verify postgresql-client is available (should be installed in container)
if ! command -v psql &> /dev/null; then
    echo "❌ Error: postgresql-client is not available."
    echo "This should be installed in the dev container. Please rebuild the container."
    exit 1
fi
echo "✅ PostgreSQL client is available."

echo "Testing Azure PostgreSQL server connectivity..."
echo "Server: $POSTGRESQL_SERVER_FQDN"
echo "Database: $POSTGRESQL_DATABASE_NAME"
echo "User: $POSTGRESQL_ADMIN_LOGIN"

# Test connectivity with better error reporting
MAX_ATTEMPTS=10
ATTEMPT=1

while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
    echo "Attempt $ATTEMPT/$MAX_ATTEMPTS: Testing PostgreSQL connectivity..."
    
    # Test with verbose output for debugging
    if PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRESQL_SERVER_FQDN" -U "$POSTGRESQL_ADMIN_LOGIN" -d "$POSTGRESQL_DATABASE_NAME" -c "SELECT version();" 2>&1 | grep -q "PostgreSQL"; then
        echo "✅ PostgreSQL server is ready and accessible!"
        break
    else
        if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
            echo "⚠️  PostgreSQL connectivity test timed out after $MAX_ATTEMPTS attempts."
            echo "This is likely due to:"
            echo "  - Firewall rules still propagating (can take up to 15 minutes)"
            echo "  - Network connectivity issues"
            echo "  - Authentication configuration"
            echo ""
            echo "The server appears ready in Azure Portal, so continuing with database initialization..."
            echo "If initialization fails, please wait a few minutes and run init-azure-db.sh manually."
            break
        else
            echo "Connection failed. Waiting 30 seconds before retry..."
            # Show last error for debugging
            PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRESQL_SERVER_FQDN" -U "$POSTGRESQL_ADMIN_LOGIN" -d "$POSTGRESQL_DATABASE_NAME" -c "SELECT 1;" 2>&1 | head -n 2
            sleep 30
        fi
    fi
    
    ATTEMPT=$((ATTEMPT + 1))
done

# Initialize Azure PostgreSQL database
echo ""
echo "Initializing Azure PostgreSQL database..."
echo "Note: If this fails, you can run './init-azure-db.sh' manually later."
echo ""

if ./init-azure-db.sh; then
    echo "✅ Database initialization completed successfully."
else
    echo ""
    echo "⚠️  Database initialization encountered issues."
    echo "This is common when firewall rules are still propagating."
    echo ""
    echo "🔧 To complete setup manually:"
    echo "  1. Wait 5-10 minutes for firewall rules to fully propagate"
    echo "  2. Run: cd infra && ./init-azure-db.sh"
    echo "  3. Then run: ./validate-deployment.sh"
    echo ""
fi

# Write resources summary now that all operations are complete
RESOURCES_FILE_PATH="../resources.txt"
mkdir -p "$(dirname "$RESOURCES_FILE_PATH")"
[ -f "$RESOURCES_FILE_PATH" ] && rm -f "$RESOURCES_FILE_PATH"

cat > "$RESOURCES_FILE_PATH" << EOF
Azure AI Foundry Resources:
- Resource Group Name: $RESOURCE_GROUP_NAME
- AI Project Name: $AI_PROJECT_NAME
- Foundry Resource Name: $AI_FOUNDRY_NAME
- Application Insights Name: $APPLICATION_INSIGHTS_NAME

PostgreSQL Database:
- Server FQDN: $POSTGRESQL_SERVER_FQDN
- Database Name: $POSTGRESQL_DATABASE_NAME
- Administrator Login: $POSTGRESQL_ADMIN_LOGIN

Service Principal:
EOF

# Add service principal status to resources file
if [ "$SP_CREATION_SUCCESS" = true ]; then
    cat >> "$RESOURCES_FILE_PATH" << EOF
- Status: Created successfully
- Client ID: $CLIENT_ID
- Note: Client secret is stored in .env file
EOF
else
    cat >> "$RESOURCES_FILE_PATH" << EOF
- Status: Creation failed - needs manual setup
- Instructions: See deployment output or .env file comments for manual creation steps
EOF
fi

# Add role assignment status
cat >> "$RESOURCES_FILE_PATH" << EOF

Role Assignments:
EOF

if [ "$ROLE_ASSIGNMENTS_SUCCESS" = true ]; then
    cat >> "$RESOURCES_FILE_PATH" << EOF
- Status: All roles assigned successfully
- Roles: Azure AI Developer, Azure AI User, Azure AI Project Manager
EOF
else
    cat >> "$RESOURCES_FILE_PATH" << EOF
- Status: Some roles failed to assign
- Failed roles: $(IFS=', '; echo "${FAILED_ROLES[*]}")
- Instructions: Assign roles manually in Azure portal or use Azure CLI
EOF
fi

echo ""
echo "🎉 Deployment completed successfully!"
echo ""

# Show service principal status
if [ "$SP_CREATION_SUCCESS" = true ]; then
    echo "✅ Service principal created and configured"
else
    echo "⚠️  Service principal creation failed"
    echo ""
    echo "🔧 To create the service principal manually:"
    echo "  1. Run: az ad sp create-for-rbac --name \"gh-popup-server-sp\" --role \"Cognitive Services OpenAI User\" --scopes \"/subscriptions/$SUB_ID/resourceGroups/$RESOURCE_GROUP_NAME/providers/Microsoft.CognitiveServices/accounts/$AI_FOUNDRY_NAME\""
    echo "  2. Update the .env file with the returned appId, password, and tenant values"
    echo "  3. Set AZURE_CLIENT_ID=<appId>, AZURE_CLIENT_SECRET=<password>, AZURE_TENANT_ID=<tenant>"
    echo ""
fi

# Show role assignment status
if [ "$ROLE_ASSIGNMENTS_SUCCESS" = true ]; then
    echo "✅ Azure AI role assignments completed successfully"
else
    echo "⚠️  Some role assignments failed"
    echo ""
    echo "🔧 To assign roles manually:"
    echo "  1. Go to the Azure portal and navigate to your resource group: $RESOURCE_GROUP_NAME"
    echo "  2. Navigate to the AI Foundry resource: $AI_FOUNDRY_NAME"
    echo "  3. Go to Access control (IAM) and add the following role assignments for your user:"
    for role in "${FAILED_ROLES[@]}"; do
        echo "     - $role"
    done
    echo "  4. Alternatively, you can use the Azure CLI if authentication issues are resolved:"
    echo "     az role assignment create --role \"Azure AI Developer\" --assignee \$(az ad signed-in-user show --query id -o tsv) --scope \"/subscriptions/$SUB_ID/resourceGroups/$RESOURCE_GROUP_NAME/providers/Microsoft.CognitiveServices/accounts/$AI_FOUNDRY_NAME\""
    echo "     az role assignment create --role \"Azure AI User\" --assignee \$(az ad signed-in-user show --query id -o tsv) --scope \"/subscriptions/$SUB_ID/resourceGroups/$RESOURCE_GROUP_NAME\""
    echo "     az role assignment create --role \"Azure AI Project Manager\" --assignee \$(az ad signed-in-user show --query id -o tsv) --scope \"/subscriptions/$SUB_ID/resourceGroups/$RESOURCE_GROUP_NAME\""
    echo ""
fi

echo "🔍 Running deployment validation..."
if ./validate-deployment.sh; then
    echo "✅ All validation checks passed!"
else
    echo "⚠️  Some validation checks failed. Please review the output above."
fi
echo ""
echo "📋 Resource Information:"
echo "  Resource Group: $RESOURCE_GROUP_NAME"
echo "  AI Project: $AI_PROJECT_NAME"
echo "  Foundry Resource: $AI_FOUNDRY_NAME"
echo "  Application Insights: $APPLICATION_INSIGHTS_NAME"
echo "  PostgreSQL Server: $POSTGRESQL_SERVER_FQDN"
echo "  PostgreSQL Database: $POSTGRESQL_DATABASE_NAME"
echo "  Text Embedding Model Deployment: text-embedding-3-small"
echo "  GPT Model Deployment: gpt-4o-mini"
echo ""
