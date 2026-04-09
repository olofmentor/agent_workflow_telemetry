// Azure-side resources that complement Databricks Terraform in ../terraform/.
// Scope: existing resource group. Do not duplicate Unity Catalog / warehouse here —
// those stay in Terraform (Databricks provider).
targetScope = 'resourceGroup'

@description('Azure region (defaults to the resource group location)')
param location string = resourceGroup().location

@description('Prefix for nested module resources (e.g. dev, prod)')
param baseName string

module identity 'modules/identity.bicep' = {
  name: 'tracing-identity'
  params: {
    location: location
    baseName: baseName
  }
}

@description('Use this identity for Azure Key Vault, storage RBAC, or federated credentials to Databricks / SP.')
output managedIdentityId string = identity.outputs.id
output managedIdentityName string = identity.outputs.name
output managedIdentityPrincipalId string = identity.outputs.principalId
output managedIdentityClientId string = identity.outputs.clientId

// When you add an Azure Databricks workspace via Bicep, expose:
// output databricksWorkspaceUrl ...
