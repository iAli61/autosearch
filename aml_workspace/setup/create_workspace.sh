#!/bin/bash

# Set default config file path
CONFIG_FILE="../config/dev.json"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --config)
        CONFIG_FILE="$2"
        shift
        shift
        ;;
        *)
        echo "Unknown option: $1"
        exit 1
        ;;
    esac
done

# Check if config file exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: Config file not found: $CONFIG_FILE"
    exit 1
fi

# Read configuration
SUBSCRIPTION_ID=$(jq -r .subscription_id "$CONFIG_FILE")
RESOURCE_GROUP=$(jq -r .resource_group "$CONFIG_FILE")
WORKSPACE_NAME=$(jq -r .workspace_name "$CONFIG_FILE")
LOCATION=$(jq -r .location "$CONFIG_FILE")
IDENTITY_NAME=$(jq -r .identity.name "$CONFIG_FILE")

# Check if subscription ID is provided
if [ -z "$SUBSCRIPTION_ID" ] || [ "$SUBSCRIPTION_ID" == "null" ]; then
    echo "Error: Please set subscription_id in $CONFIG_FILE"
    exit 1
fi

# Set subscription
echo "Setting Azure subscription..."
az account set -s "$SUBSCRIPTION_ID"

# Create resource group if it doesn't exist
echo "Creating resource group if it doesn't exist..."
az group create \
    --subscription "$SUBSCRIPTION_ID" \
    --name "$RESOURCE_GROUP" \
    --location "$LOCATION" \
    --tags $(jq -r '.tags | to_entries | map("\(.key)=\(.value)") | join(" ")' "$CONFIG_FILE")

# Create managed identity if it doesn't exist
echo "Creating managed identity if it doesn't exist..."
az identity create --name "$IDENTITY_NAME" --resource-group "$RESOURCE_GROUP" --location "$LOCATION"

# Get managed identity ID and principal ID
IDENTITY_ID=$(az identity show --name "$IDENTITY_NAME" --resource-group "$RESOURCE_GROUP" --query 'id' -o tsv)
PRINCIPAL_ID=$(az identity show --name "$IDENTITY_NAME" --resource-group "$RESOURCE_GROUP" --query 'principalId' -o tsv)

# Check if workspace exists
WORKSPACE_EXISTS=$(az ml workspace show \
    --subscription "$SUBSCRIPTION_ID" \
    --resource-group "$RESOURCE_GROUP" \
    --name "$WORKSPACE_NAME" \
    2>/dev/null)

if [ -z "$WORKSPACE_EXISTS" ]; then
    # Create workspace
    echo "Creating Azure ML workspace..."
    az ml workspace create \
        --name "$WORKSPACE_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --location "$LOCATION" \
        # --storage-account "$STORAGE_ID"
else
    echo "Azure ML workspace already exists: $WORKSPACE_NAME"
fi

# Wait for workspace to be ready
echo "Waiting for workspace to be ready..."
sleep 30

# Get storage account name from workspace details
STORAGE_ACCOUNT=$(az ml workspace show \
    --subscription "$SUBSCRIPTION_ID" \
    --resource-group "$RESOURCE_GROUP" \
    --name "$WORKSPACE_NAME" \
    --query 'storage_account' -o tsv | awk -F/ '{print $NF}')

# Get storage account ID
STORAGE_ACCOUNT_ID=$(az storage account show --name "$STORAGE_ACCOUNT" --resource-group "$RESOURCE_GROUP" --query 'id' -o tsv)

# print storage account id
echo "Storage account id: $STORAGE_ACCOUNT_ID"

# Assign roles to managed identity
echo "Assigning roles to managed identity..."
az role assignment create --assignee-object-id "$PRINCIPAL_ID" --assignee-principal-type ServicePrincipal --role "Storage Blob Data Reader" --scope "$STORAGE_ACCOUNT_ID"
az role assignment create --assignee-object-id "$PRINCIPAL_ID" --assignee-principal-type ServicePrincipal --role "Storage Blob Data Contributor" --scope "$STORAGE_ACCOUNT_ID"

# Assign Contributor role to the managed identity for the Azure ML workspace
WORKSPACE_ID=$(az ml workspace show --subscription "$SUBSCRIPTION_ID" --resource-group "$RESOURCE_GROUP" --name "$WORKSPACE_NAME" --query 'id' -o tsv)
az role assignment create --assignee-object-id "$PRINCIPAL_ID" --assignee-principal-type ServicePrincipal --role "Contributor" --scope "$WORKSPACE_ID"

# Create compute clusters
echo "Creating compute clusters..."

# CPU cluster
CPU_CLUSTER_NAME=$(jq -r .compute.cpu_cluster.name "$CONFIG_FILE")
CPU_VM_SIZE=$(jq -r .compute.cpu_cluster.vm_size "$CONFIG_FILE")
CPU_MIN_INSTANCES=$(jq -r .compute.cpu_cluster.min_instances "$CONFIG_FILE")
CPU_MAX_INSTANCES=$(jq -r .compute.cpu_cluster.max_instances "$CONFIG_FILE")
CPU_IDLE_TIME=$(jq -r .compute.cpu_cluster.idle_time_before_scale_down "$CONFIG_FILE")
CPU_LOW_PRIORITY=$(jq -r .compute.cpu_cluster.low_priority "$CONFIG_FILE")

# Create CPU compute YAML configuration
cat << EOF > cpu_compute.yml
name: $CPU_CLUSTER_NAME
type: amlcompute
size: $CPU_VM_SIZE
min_instances: $CPU_MIN_INSTANCES
max_instances: $CPU_MAX_INSTANCES
idle_time_before_scale_down: $CPU_IDLE_TIME
identity:
  type: user_assigned
  user_assigned_identities: 
    - resource_id: $IDENTITY_ID
EOF

if [ "$CPU_LOW_PRIORITY" == "true" ]; then
    sed -i '/type: amlcompute/a \
tier: low_priority' cpu_compute.yml
fi

# Create CPU compute cluster
az ml compute create \
    --resource-group "$RESOURCE_GROUP" \
    --workspace-name "$WORKSPACE_NAME" \
    --file cpu_compute.yml

# GPU cluster
GPU_CLUSTER_NAME=$(jq -r .compute.gpu_cluster.name "$CONFIG_FILE")
GPU_VM_SIZE=$(jq -r .compute.gpu_cluster.vm_size "$CONFIG_FILE")
GPU_MIN_INSTANCES=$(jq -r .compute.gpu_cluster.min_instances "$CONFIG_FILE")
GPU_MAX_INSTANCES=$(jq -r .compute.gpu_cluster.max_instances "$CONFIG_FILE")
GPU_IDLE_TIME=$(jq -r .compute.gpu_cluster.idle_time_before_scale_down "$CONFIG_FILE")
GPU_LOW_PRIORITY=$(jq -r .compute.gpu_cluster.low_priority "$CONFIG_FILE")

# Create GPU compute YAML configuration
cat << EOF > gpu_compute.yml
name: $GPU_CLUSTER_NAME
type: amlcompute
size: $GPU_VM_SIZE
min_instances: $GPU_MIN_INSTANCES
max_instances: $GPU_MAX_INSTANCES
idle_time_before_scale_down: $GPU_IDLE_TIME
identity:
  type: user_assigned
  user_assigned_identities: 
    - resource_id: $IDENTITY_ID
EOF

if [ "$GPU_LOW_PRIORITY" == "true" ]; then
    sed -i '/type: amlcompute/a \
tier: low_priority' gpu_compute.yml
fi

# Create GPU compute cluster
az ml compute create \
    --resource-group "$RESOURCE_GROUP" \
    --workspace-name "$WORKSPACE_NAME" \
    --file gpu_compute.yml

# Parse the “compute_instances” array and create each compute instance.
COMPUTE_INSTANCES=$(jq -c '.compute.compute_instances[]?' "$CONFIG_FILE")
for ci in $COMPUTE_INSTANCES; do
    CI_NAME=$(echo "$ci" | jq -r '.name')
    CI_VM_SIZE=$(echo "$ci" | jq -r '.vm_size')
    echo "Creating compute instance $CI_NAME..."
    az ml compute create \
        --name "$CI_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --workspace-name "$WORKSPACE_NAME" \
        --type computeinstance \
        --size "$CI_VM_SIZE"
done

# Clean up temporary YAML files
rm cpu_compute.yml gpu_compute.yml

echo "Setup complete!"