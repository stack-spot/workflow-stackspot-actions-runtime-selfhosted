import json
from pathlib import Path
from ruamel.yaml import YAML
from io import StringIO
from typing import Dict
from oscli.core.http import post_with_authorization
from oscli.core.http import get_with_authorization

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


def save_output(name: str, value: str):
    with open("rollback-output.log", 'a') as output_file:
        print(f'{name}={value}', file=output_file)


def get_env_id(slug):
    
    env_request = get_with_authorization(url=f"https://workspace-workspace-api.stg.stackspot.com/v1/environments", 
                                            headers={'Content-Type': 'application/json' },
                                            timeout=20)

    if env_request.status_code != 200:
        print("Unable to fetch Environments data")
        print("- Status:", env_request.status_code)
        print("- Error:", env_request.reason)
        print("- Response:", env_request.text)
        exit(1)
    
    env_list = env_request.json()
    
    for env in env_list:
        if env["name"] == slug:
            return env["id"]
        
    print(f"Unable to find environment: {slug}")
    exit(1)


def run(metadata):

    TF_STATE_BUCKET_NAME = metadata.inputs.get("tf_state_bucket_name")
    TF_STATE_REGION = metadata.inputs.get("tf_state_region")
    IAC_BUCKET_NAME = metadata.inputs.get("iac_bucket_name")
    IAC_REGION = metadata.inputs.get("iac_region")
    VERBOSE = metadata.inputs.get("verbose")
    VERSION_TAG = metadata.inputs.get("version_tag")
    ENVIRONMENT = metadata.inputs.get("environment")

    inputs_list = [ENVIRONMENT, VERSION_TAG, TF_STATE_BUCKET_NAME, TF_STATE_REGION, IAC_BUCKET_NAME, IAC_REGION]

    if None in inputs_list:
        print("- Some mandatory input is empty. Please, check the input list.")
        exit(1)

    with open(Path('.stk/stk.yaml'), 'r') as file:
        stk_yaml = file.read()

    stk_dict = safe_load(stk_yaml)

    if VERBOSE is not None:
        print("- stk.yaml:", stk_dict)

    stk_yaml_type = stk_dict["spec"]["type"]
    app_or_infra_id = stk_dict["spec"]["infra-id"] if stk_yaml_type == "infra" else stk_dict["spec"]["app-id"]

    print(f"{stk_yaml_type} project identified, with ID: {app_or_infra_id}")

        
    stk_id = {
        "appId":  app_or_infra_id,
    } if stk_yaml_type != "infra" else {
        "infraId": app_or_infra_id,
    }

    request_data = {
        **stk_id,
        "envId": get_env_id(ENVIRONMENT),
        "tag": VERSION_TAG,
        "config": {
            "tfstate": {
                "bucket": TF_STATE_BUCKET_NAME,
                "region": TF_STATE_REGION
            },
            "iac": {
                "bucket": IAC_BUCKET_NAME,
                "region": IAC_REGION
            }
        },
        "pipelineUrl": "http://stackspot.com"
    }

    if VERBOSE is not None:
        print("- ROLLBACK RUN REQUEST DATA:", request_data)
    

    print("Deploying Self-Hosted Rollback..")

    rollback_request = post_with_authorization(url=f"https://runtime-manager.stg.stackspot.com/v1/run/self-hosted/rollback/{stk_yaml_type}", 
                                 body=request_data, 
                                 headers={'Content-Type': 'application/json' },
                                 timeout=20)
    

    if rollback_request.status_code == 201:
        d2 = rollback_request.json()
        runId = d2["runId"]
        runType = d2["runType"]
        tasks = d2["tasks"]

        save_output('tasks', tasks)
        save_output('run_id', runId)

        print(f"- Rollback RUN {runType} successfully started with ID: {runId}")
        print(f"- Rollback RUN TASKS LIST: {tasks}")

    else:
        print("- Error starting self hosted rollback run")
        print("- Status:", rollback_request.status_code)
        print("- Error:", rollback_request.reason)
        print("- Response:", rollback_request.text)
        exit(1)