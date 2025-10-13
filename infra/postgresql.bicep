@description('Name of the PostgreSQL server')
param postgresqlServerName string

@description('Location for the PostgreSQL server')
param location string = resourceGroup().location

@description('PostgreSQL server administrator username')
param administratorLogin string = 'postgres'

@description('PostgreSQL server administrator password')
@secure()
param administratorPassword string

@description('PostgreSQL server version')
param postgresqlVersion string = '17'

@description('PostgreSQL server SKU name')
param skuName string = 'Standard_B1ms'

@description('PostgreSQL server tier')
param skuTier string = 'Burstable'

@description('Storage size in GB')
param storageSizeGB int = 32

@description('Set of tags to apply to all resources')
param tags object = {}

@description('Database name to create')
param databaseName string = 'zava'

@description('Allowed IP addresses for firewall rules')
param allowedIPRanges array = [
  {
    name: 'AllowAllAzureServices'
    startIpAddress: '0.0.0.0'
    endIpAddress: '0.0.0.0'
  }
  // Note: This allows all internet access for workshop/demo purposes
  // In production, restrict this to specific IP ranges
  {
    name: 'AllowAllInternetAccess'
    startIpAddress: '0.0.0.0'
    endIpAddress: '255.255.255.255'
  }
]

// PostgreSQL Flexible Server
resource postgresqlServer 'Microsoft.DBforPostgreSQL/flexibleServers@2023-06-01-preview' = {
  name: postgresqlServerName
  location: location
  tags: tags
  sku: {
    name: skuName
    tier: skuTier
  }
  properties: {
    version: postgresqlVersion
    administratorLogin: administratorLogin
    administratorLoginPassword: administratorPassword
    storage: {
      storageSizeGB: storageSizeGB
      autoGrow: 'Enabled'
    }
    backup: {
      backupRetentionDays: 7
      geoRedundantBackup: 'Disabled'
    }
    network: {
      publicNetworkAccess: 'Enabled'
    }
    highAvailability: {
      mode: 'Disabled'
    }
    maintenanceWindow: {
      customWindow: 'Disabled'
      dayOfWeek: 0
      startHour: 0
      startMinute: 0
    }
    authConfig: {
      activeDirectoryAuth: 'Disabled'
      passwordAuth: 'Enabled'
    }
  }
}

// Enable pgvector extension
resource pgvectorExtension 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2023-06-01-preview' = {
  name: 'azure.extensions'
  parent: postgresqlServer
  properties: {
    value: 'VECTOR,PLPGSQL'
    source: 'user-override'
  }
}

// Create database
resource database 'Microsoft.DBforPostgreSQL/flexibleServers/databases@2023-06-01-preview' = {
  name: databaseName
  parent: postgresqlServer
  dependsOn: [pgvectorExtension]
  properties: {
    charset: 'UTF8'
    collation: 'en_US.utf8'
  }
}

// Firewall rules
resource firewallRules 'Microsoft.DBforPostgreSQL/flexibleServers/firewallRules@2023-06-01-preview' = [for rule in allowedIPRanges: {
  name: rule.name
  parent: postgresqlServer
  properties: {
    startIpAddress: rule.startIpAddress
    endIpAddress: rule.endIpAddress
  }
}]

// Outputs
output serverName string = postgresqlServer.name
output serverFqdn string = postgresqlServer.properties.fullyQualifiedDomainName
output databaseName string = database.name
output administratorLogin string = administratorLogin
