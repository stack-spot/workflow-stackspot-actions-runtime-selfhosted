import os
import json
from pathlib import Path
from ruamel.yaml import YAML
from io import StringIO
from typing import Dict
from oscli.core.http import post_with_authorization
from oscli.core.http import get_with_authorization
from sys import exit

# Constants
STK_RUNTIME_MANAGER_DOMAIN = os.getenv(
    "STK_RUNTIME_MANAGER_DOMAIN", "https://runtime-manager.v1.stackspot.com"
)
STK_WORKSPACE_DOMAIN = os.getenv(
    "STK_WORKSPACE_DOMAIN", "https://runtime-manager.v1.stackspot.com"
)
STK_FILE = ".stk/stk.yaml"
OUTPUT_FILE = "rollback-output.log"
HEADERS = {"Content-Type": "application/json"}
TIMEOUT = 20


def yaml() -> YAML:
    yml = YAML()
    yml.indent(mapping=2, sequence=4, offset=2)
    yml.allow_unicode = True
    yml.default_flow_style = False
    yml.preserve_quotes = True
    return yml


def safe_load(content: str) -> dict:
    yml = yaml()
    return yml.load(StringIO(content))


def get_stk_yaml() -> dict:
    try:
        with open(Path(STK_FILE), "r") as file:
            stk_yaml = file.read()
        stk_yaml = safe_load(stk_yaml)
        return stk_yaml
    except FileNotFoundError:
        print(f"> Error: {STK_FILE} not found.")
        exit(1)
    except Exception as e:
        print(f"> Error reading {STK_FILE}: {e}")
        exit(1)


def save_output(value: dict):

    with open(OUTPUT_FILE, "w") as output_file:
        json.dump(value, output_file, indent=4)
    print(f"> Output saved to {OUTPUT_FILE}")


def build_request(action_inputs: dict, env_id: str, stk_yaml: dict) -> dict:

    try:
        # Extract the type of deployment (app or infra) from the stack YAML configuration
        type = get_type(stk_yaml)

        # Define a parser to map the type to the appropriate key and value for the request payload
        type_parser = {
            "app": {"key": "appId", "value": stk_yaml["spec"].get("app-id")},
            "infra": {"key": "infraId", "value": stk_yaml["spec"].get("infra-id")},
        }

        # Build the request payload using the provided inputs and the parsed type information
        request_data = {
            f"{type_parser[type]['key']}": type_parser[type]["value"],
            "envId": env_id,
            "tag": action_inputs["version_tag"],
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

        print(
            f"> Runtime manager run self hosted rollback request data:\n{json.dumps(request_data, indent=4)}"
        )
        return request_data
    except KeyError as e:
        print(f"> Error: Missing required input {e}")
        exit(1)


def get_type(stk_yaml: dict) -> str:
    return stk_yaml["spec"]["type"]


def runtime_manager_run_self_hosted_rollback(
    request_data: dict, stk_yaml: dict, version_tag: str
):

    type = get_type(stk_yaml)
    url = f"{STK_RUNTIME_MANAGER_DOMAIN}/v1/run/self-hosted/rollback/{type}"

    print("> Calling runtime manager to rollback tasks...")
    response = post_with_authorization(
        url=url, body=request_data, headers=HEADERS, timeout=TIMEOUT
    )

    if response.ok:
        if response.status_code == 201:
            response_data = response.json()
            print(
                f"> Rollback successfully started:\n{json.dumps(response_data, indent=4)}"
            )
        else:
            print(
                f"> Rollback successfully but no modifications detected for tag {version_tag}"
            )
            response_data = {}

        save_output(response_data)

    else:
        print(
            f"> Error: Failed to start self-hosted rollback run. Status: {response.status_code}"
        )
        print(f"> Response: {response.text}")
        exit(1)


def get_environment_id(environment_slug):

    url = f"{STK_WORKSPACE_DOMAIN}/v1/environments"

    print("> Calling workspace to load environments...")
    response = get_with_authorization(url=url, headers=HEADERS, timeout=TIMEOUT)

    if response.ok:
        env_list = response.json()
        for env in env_list:
            if env["name"] == environment_slug:
                return env["id"]

    else:
        print(f"> Error: Failed to load environments. Status: {response.status_code}")
        print(f"> Response: {response.text}")
        exit(1)


def run(metadata):
    # Load the manifest file
    stk_yaml = get_stk_yaml()

    # Load environment Id
    env_id = get_environment_id(metadata.inputs.get("environment"))

    # Build the request data
    request = build_request(metadata.inputs, env_id, stk_yaml)

    # Execute the rollback request
    runtime_manager_run_self_hosted_rollback(
        request, stk_yaml, metadata.inputs["version_tag"]
    )
