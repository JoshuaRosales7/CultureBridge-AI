// Bicep template for CultureBridge AI Azure infrastructure
// Deploys: Azure OpenAI, Key Vault, Application Insights, Static Web Apps, Function App

@description('The location for all resources')
param location string = resourceGroup().location

@description('Environment name (dev, staging, prod)')
@allowed(['dev', 'staging', 'prod'])
param environment string = 'dev'

@description('Project name prefix')
param projectName string = 'culturebridge'

@description('Azure OpenAI model deployment name')
param openAIDeploymentName string = 'gpt-4o'

// ---------- Variables ----------
var uniqueSuffix = uniqueString(resourceGroup().id)
var baseName = '${projectName}-${environment}'

// ---------- Log Analytics Workspace ----------
resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: '${baseName}-logs-${uniqueSuffix}'
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

// ---------- Application Insights ----------
resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: '${baseName}-insights-${uniqueSuffix}'
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalytics.id
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
}

// ---------- Key Vault ----------
resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: '${baseName}-kv-${uniqueSuffix}'
  location: location
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    enableRbacAuthorization: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 7
    enablePurgeProtection: false // Set to true for production
    networkAcls: {
      defaultAction: 'Allow' // Restrict in production
      bypass: 'AzureServices'
    }
  }
}

// ---------- Azure OpenAI ----------
resource openAI 'Microsoft.CognitiveServices/accounts@2024-04-01-preview' = {
  name: '${baseName}-oai-${uniqueSuffix}'
  location: location
  kind: 'OpenAI'
  sku: {
    name: 'S0'
  }
  properties: {
    customSubDomainName: '${baseName}-oai-${uniqueSuffix}'
    publicNetworkAccess: 'Enabled'
    networkAcls: {
      defaultAction: 'Allow'
    }
  }
}

resource openAIDeployment 'Microsoft.CognitiveServices/accounts/deployments@2024-04-01-preview' = {
  parent: openAI
  name: openAIDeploymentName
  sku: {
    name: 'Standard'
    capacity: 30
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: 'gpt-4o'
      version: '2024-08-06'
    }
  }
}

// ---------- Storage Account (for Function App) ----------
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: '${replace(baseName, '-', '')}st${uniqueSuffix}'
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    supportsHttpsTrafficOnly: true
    minimumTlsVersion: 'TLS1_2'
  }
}

// ---------- App Service Plan ----------
resource appServicePlan 'Microsoft.Web/serverfarms@2023-12-01' = {
  name: '${baseName}-plan-${uniqueSuffix}'
  location: location
  sku: {
    name: 'Y1'
    tier: 'Dynamic'
  }
  properties: {
    reserved: true // Linux
  }
}

// ---------- Function App (API) ----------
resource functionApp 'Microsoft.Web/sites@2023-12-01' = {
  name: '${baseName}-api-${uniqueSuffix}'
  location: location
  kind: 'functionapp,linux'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: appServicePlan.id
    httpsOnly: true
    siteConfig: {
      pythonVersion: '3.11'
      linuxFxVersion: 'PYTHON|3.11'
      appSettings: [
        {
          name: 'AzureWebJobsStorage'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};AccountKey=${storageAccount.listKeys().keys[0].value}'
        }
        {
          name: 'FUNCTIONS_EXTENSION_VERSION'
          value: '~4'
        }
        {
          name: 'FUNCTIONS_WORKER_RUNTIME'
          value: 'python'
        }
        {
          name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
          value: appInsights.properties.ConnectionString
        }
        {
          name: 'AZURE_OPENAI_ENDPOINT'
          value: openAI.properties.endpoint
        }
        {
          name: 'AZURE_OPENAI_DEPLOYMENT'
          value: openAIDeploymentName
        }
        {
          name: 'AZURE_KEYVAULT_URL'
          value: keyVault.properties.vaultUri
        }
      ]
    }
  }
}

// ---------- Key Vault Access for Function App ----------
resource kvRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(keyVault.id, functionApp.id, 'Key Vault Secrets User')
  scope: keyVault
  properties: {
    principalId: functionApp.identity.principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '4633458b-17de-408a-b874-0445c86b69e6') // Key Vault Secrets User
    principalType: 'ServicePrincipal'
  }
}

// ---------- Static Web App (Frontend) ----------
resource staticWebApp 'Microsoft.Web/staticSites@2023-12-01' = {
  name: '${baseName}-web-${uniqueSuffix}'
  location: location
  sku: {
    name: 'Free'
    tier: 'Free'
  }
  properties: {
    buildProperties: {
      appLocation: '/apps/web'
      outputLocation: '.next'
    }
  }
}

// ---------- Outputs ----------
output functionAppName string = functionApp.name
output functionAppUrl string = 'https://${functionApp.properties.defaultHostName}'
output staticWebAppName string = staticWebApp.name
output staticWebAppUrl string = 'https://${staticWebApp.properties.defaultHostname}'
output appInsightsName string = appInsights.name
output appInsightsConnectionString string = appInsights.properties.ConnectionString
output keyVaultName string = keyVault.name
output keyVaultUri string = keyVault.properties.vaultUri
output openAIEndpoint string = openAI.properties.endpoint
