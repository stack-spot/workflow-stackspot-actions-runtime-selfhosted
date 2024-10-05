## runtime-manager-self-hosted-deploy

This action is responsible for managing and executing a self-hosted deployment using the StackSpot Runtime Manager. It reads a manifest file, builds the necessary request data, and sends it to the Runtime Manager to initiate the deployment process.

## Requirements

Before using this action, ensure that you have the following:

- **StackSpot CLI** installed and configured.
- A valid `manifest.yaml` file in the root directory of your project.
- The following environment variables set:
  - `STK_RUNTIME_MANAGER_DOMAIN`: The domain for the StackSpot Runtime Manager (default: `https://runtime-manager.v1.stackspot.com`).
- The following inputs provided:
  - `tf_state_bucket_name`: The name of the bucket for Terraform state.
  - `tf_state_region`: The region of the Terraform state bucket.
  - `iac_bucket_name`: The name of the bucket for Infrastructure as Code (IaC).
  - `iac_region`: The region of the IaC bucket.

## Usage

To use the `runtime-manager-self-hosted-deploy` action, follow these steps:

1. Ensure you have the required inputs:
   - **tf_state_bucket_name**: The name of the bucket for Terraform state.
   - **tf_state_region**: The region of the Terraform state bucket.
   - **iac_bucket_name**: The name of the bucket for Infrastructure as Code (IaC).
   - **iac_region**: The region of the IaC bucket.

2. Ensure you have a valid `manifest.yaml` file in the root directory of your project. This file should contain the necessary deployment information.

3. Run the action using the StackSpot CLI or integrate it into your CI/CD pipeline.

### Example:

```bash
stk run action /path/to/runtime-manager-self-hosted-deploy