## runtime-create-manifest-action

This action is responsible for creating a manifest for deployment in a specified environment and workspace. It allows users to specify a version tag and optionally provide a path to an OpenAPI file and dynamic inputs.

## Requirements

Before using this action, ensure that you have the following:

- StackSpot CLI installed and configured.
- A valid workspace and environment where the deployment will take place.
- (Optional) An OpenAPI file if you want to publish it to the StackSpot Catalog API.
- (Optional) Dynamic inputs in the form of key-value pairs.

## Usage

To use the `runtime-create-manifest-action`, follow these steps:

1. Ensure you have the required inputs:
   - **Environment**: The environment where the deployment will occur.
   - **Workspace**: The workspace to be used for the deployment.
   - **Version Tag**: The version tag for the deployment.
   - **OpenAPI Path** (optional): The path to the OpenAPI file to publish on StackSpot Catalog API.
   - **Dynamic Inputs** (optional): Additional dynamic inputs in the form of key-value pairs (e.g., `--key1 value1 --key2 value2`).

2. Run the action using the StackSpot CLI:
   ```bash
   stk run action /path/to/runtime-create-manifest-action