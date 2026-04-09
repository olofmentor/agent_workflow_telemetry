@description('Azure region for the managed identity')
param location string

@description('Stable prefix used in the user-assigned identity name')
param baseName string

resource uai 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: '${baseName}-tracing-mi'
  location: location
}

output id string = uai.id
output name string = uai.name
output principalId string = uai.properties.principalId
output clientId string = uai.properties.clientId
