#!/bin/bash
set -e

# Cleanup script for Azure resources
# This script removes all resources created by the deployment

echo "🧹 Azure Resources Cleanup Script"
echo "================================="

# Load resource information
RESOURCES_FILE="../resources.txt"

if [ ! -f "$RESOURCES_FILE" ]; then
    echo "❌ Error: resources.txt file not found."
    echo "This file is created during deployment and contains resource information."
    echo "You can still manually delete the resource group if you know its name."
    exit 1
fi

echo "Reading resource information from $RESOURCES_FILE..."
RESOURCE_GROUP_NAME=$(grep "Resource Group Name:" "$RESOURCES_FILE" | cut -d: -f2 | tr -d ' ')

if [ -z "$RESOURCE_GROUP_NAME" ]; then
    echo "❌ Error: Could not find resource group name in resources.txt"
    exit 1
fi

echo "Found resource group: $RESOURCE_GROUP_NAME"
echo ""

# Confirm deletion
echo "⚠️  WARNING: This will permanently delete ALL resources in the resource group:"
echo "  - Resource Group: $RESOURCE_GROUP_NAME"
echo "  - Azure AI Foundry resources"
echo "  - PostgreSQL database and all data"
echo "  - Application Insights"
echo "  - Service principal"
echo ""

read -p "Are you sure you want to delete all resources? Type 'yes' to confirm: " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Cleanup cancelled."
    exit 0
fi

echo ""
echo "🗑️  Deleting Azure resources..."

# Check if resource group exists
if az group show --name "$RESOURCE_GROUP_NAME" > /dev/null 2>&1; then
    echo "Deleting resource group: $RESOURCE_GROUP_NAME"
    
    # Delete the resource group (this deletes all resources within it)
    if az group delete --name "$RESOURCE_GROUP_NAME" --yes --no-wait; then
        echo "✅ Resource group deletion initiated."
        echo "   The deletion is running in the background and may take several minutes."
    else
        echo "❌ Failed to delete resource group."
        exit 1
    fi
else
    echo "⚠️  Resource group $RESOURCE_GROUP_NAME not found. It may have already been deleted."
fi

# Try to clean up the service principal
echo ""
echo "🔐 Cleaning up service principal..."

# Get service principal info from .env if available
if [ -f "../.env" ]; then
    CLIENT_ID=$(grep "AZURE_CLIENT_ID=" ../.env | cut -d= -f2 | tr -d '"')
    
    if [ -n "$CLIENT_ID" ] && [ "$CLIENT_ID" != "null" ]; then
        echo "Found service principal with Client ID: $CLIENT_ID"
        
        if az ad sp show --id "$CLIENT_ID" > /dev/null 2>&1; then
            echo "Deleting service principal..."
            if az ad sp delete --id "$CLIENT_ID"; then
                echo "✅ Service principal deleted."
            else
                echo "❌ Failed to delete service principal. You may need to delete it manually."
            fi
        else
            echo "⚠️  Service principal not found. It may have already been deleted."
        fi
    else
        echo "⚠️  Could not find service principal Client ID in .env file."
    fi
else
    echo "⚠️  .env file not found. Cannot clean up service principal automatically."
fi

# Clean up local files
echo ""
echo "🧽 Cleaning up local files..."

# Remove .env file
if [ -f "../.env" ]; then
    rm "../.env"
    echo "✅ Removed .env file"
fi

# Remove resources.txt file
if [ -f "$RESOURCES_FILE" ]; then
    rm "$RESOURCES_FILE"
    echo "✅ Removed resources.txt file"
fi

echo ""
echo "🎉 Cleanup completed!"
echo ""
echo "📋 What was removed:"
echo "  ✅ Resource group and all Azure resources"
echo "  ✅ Service principal (if found)"
echo "  ✅ Local configuration files (.env, resources.txt)"
echo ""
echo "📝 Note: The resource group deletion may take several minutes to complete."
echo "You can check the status in the Azure portal or with:"
echo "  az group show --name $RESOURCE_GROUP_NAME"