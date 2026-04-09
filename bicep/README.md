# Bicep: Azure resources

These templates provision **Azure-native** resources (for example a user-assigned **managed identity**) that your team may use alongside **Databricks Terraform** in [`../terraform`](../terraform/).

| Owner | What it provisions |
|--------|---------------------|
| **Bicep (this folder)** | Resource groups (if you use subscription-level deployments), managed identities, Key Vault, storage accounts, networking, optional Azure Databricks **workspace** creation |
| **Terraform (`../terraform`)** | Databricks workspace **objects**: Unity Catalog schema for traces, SQL warehouse, grants (`databricks` provider) |

**Rule:** Do not define the same logical resource in both Bicep and Terraform.

## Deploy order

1. **Azure subscription / resource group** — create the RG if needed (`az group create`).
2. **This Bicep template** (optional) — identities, storage, workspace URL outputs you need before automation.
3. **Terraform** — point [`databricks_host`](../terraform/examples/agent_tracing/variables.tf) at your workspace URL (from Azure portal, existing Bicep output, or manual workspace). Run `terraform apply` for UC schema and SQL warehouse.
4. **Application** — copy Terraform outputs and Databricks tokens into `.env`; run `uv run python -m init` per the root [README.md](../README.md).

## Example: resource group deployment

Set variables, then deploy:

```bash
cd bicep
RESOURCE_GROUP="rg-agent-tracing-dev"
LOCATION="westeurope"
az group create --name "$RESOURCE_GROUP" --location "$LOCATION"

az deployment group create \
  --resource-group "$RESOURCE_GROUP" \
  --template-file main.bicep \
  --parameters @parameters.example.json
```

Adjust `parameters.example.json` (copy to `parameters.json` if you keep secrets out of git) or pass `--parameters baseName=myenv`.

## Outputs and Terraform

| Bicep output (when you add them) | Typical Terraform / `.env` consumer |
|----------------------------------|-------------------------------------|
| `databricksWorkspaceUrl` | `databricks_host` in `terraform.tfvars` |
| Managed identity IDs | Azure RBAC, Key Vault access, or OIDC to Databricks |
| Storage account / DFS endpoints | `storage_root` for optional [`uc_catalog`](../terraform/modules/uc_catalog) module |

See [terraform/README.md](../terraform/README.md) for the Terraform side of this handoff.
