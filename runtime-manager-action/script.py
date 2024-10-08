import os
import json
from pathlib import Path
from ruamel.yaml import YAML
from io import StringIO
from typing import Dict
from oscli.core.http import post_with_authorization

# Constants
STK_RUNTIME_MANAGER_DOMAIN = os.getenv(
    "STK_RUNTIME_MANAGER_DOMAIN", "https://runtime-manager.v1.stackspot.com"
)
TYPE_PARSER = {"application": "app", "shared-infrastructure": "infra"}
MANIFEST_FILE = "manifest.yaml"
OUTPUT_FILE = "manager-output.log"
HEADERS = {"Content-Type": "application/json"}
TIMEOUT = 20


def yaml() -> YAML:
    """
    Initializes and returns a YAML parser with specific configurations.

    Returns:
        YAML: A configured YAML parser.
    """
    yml = YAML()
    yml.indent(mapping=2, sequence=4, offset=2)
    yml.allow_unicode = True
    yml.default_flow_style = False
    yml.preserve_quotes = True
    return yml


def safe_load(content: str) -> dict:
    """
    Safely loads a YAML string into a Python dictionary.

    Args:
        content (str): The YAML content as a string.

    Returns:
        dict: The parsed YAML content as a dictionary.
    """
    yml = yaml()
    return yml.load(StringIO(content))


def get_manifest() -> dict:
    """
    Reads and parses the 'manifest.yaml' file into a dictionary.

    Returns:
        dict: The parsed manifest content.

    Raises:
        FileNotFoundError: If the 'manifest.yaml' file is not found.
    """
    try:
        with open(Path(MANIFEST_FILE), "r") as file:
            manifesto_yaml = file.read()
        manifest = safe_load(manifesto_yaml)
        return manifest
    except FileNotFoundError:
        print(f"> Error: {MANIFEST_FILE} not found.")
        exit(1)
    except Exception as e:
        print(f"> Error reading {MANIFEST_FILE}: {e}")
        exit(1)


def save_output(value: dict):
    """
    Saves the provided value to the 'manager-output.log' file.

    Args:
        value (dict): The content to be saved in the log file.
    """
    with open(OUTPUT_FILE, "w") as output_file:
        json.dump(value, output_file, indent=4)
    print(f"> Output saved to {OUTPUT_FILE}")


def build_request(action_inputs: dict, app_infra_manifest: dict) -> dict:
    """
    Builds the request data for the self-hosted deployment by merging the action inputs and manifest data.

    Args:
        action_inputs (dict): The inputs provided for the action (e.g., bucket names, regions).
        app_infra_manifest (dict): The parsed manifest data.

    Returns:
        dict: The complete request data for the deployment.
    """
    try:
        config_data = {
            "config": {
                "tfstate": {
                    "bucket": action_inputs["tf_state_bucket_name"],
                    "region": action_inputs["tf_state_region"],
                },
                "iac": {
                    "bucket": action_inputs["iac_bucket_name"],
                    "region": action_inputs["iac_region"],
                },
            },
            "pipelineUrl": "http://stackspot.com",
        }
        # Merge the manifest data with the configuration data
        request_data = {**app_infra_manifest, **config_data}
        print(
            f"> Runtime manager run self hosted deploy request data:\n{json.dumps(request_data, indent=4)}"
        )
        return request_data
    except KeyError as e:
        print(f"> Error: Missing required input {e}")
        exit(1)


def runtime_manager_run_self_hosted_deploy(request_data: dict, manifest: dict):
    """
    Sends a request to the StackSpot Runtime Manager to start a self-hosted deployment.

    Args:
        request_data (dict): The request data for the deployment.
        manifest (dict): The parsed manifest data.

    Raises:
        SystemExit: If the deployment request fails.
    """
    manifest_type = manifest["manifesto"]["kind"]
    url = f"{STK_RUNTIME_MANAGER_DOMAIN}/v1/run/self-hosted/deploy/{TYPE_PARSER[manifest_type]}"

    print("> Calling runtime manager to define tasks...")
    response = post_with_authorization(
        url=url, body=request_data, headers=HEADERS, timeout=TIMEOUT
    )

    if response.ok:
        # Parse the response and extract relevant data
        response_data = response.json()
        print(f"> Deploy successfully started:\n{json.dumps(response_data, indent=4)}")

        # Save the response to the output log
        save_output(response_data)
    else:
        print(
            f"> Error: Failed to start self-hosted deploy run. Status: {response.status_code}"
        )
        print(f"> Response: {response.text}")
        exit(1)


def run(metadata):
    # Load the manifest file
    manifest = get_manifest()

    # Build the request data
    request = build_request(metadata.inputs, manifest)

    # Execute the deployment request
    runtime_manager_run_self_hosted_deploy(request, manifest)
