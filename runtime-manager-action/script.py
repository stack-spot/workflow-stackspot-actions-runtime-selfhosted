import json
from pathlib import Path
from ruamel.yaml import YAML
from io import StringIO
from typing import Dict
from oscli.core.http import post_with_authorization

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


def save_output(value: str):
    with open("manager-output.log", 'w') as output_file:
        print(value, file=output_file)

def run(metadata):
    
    TF_STATE_BUCKET_NAME = metadata.inputs.get("tf_state_bucket_name")
    TF_STATE_REGION = metadata.inputs.get("tf_state_region")
    IAC_BUCKET_NAME = metadata.inputs.get("iac_bucket_name")
    IAC_REGION = metadata.inputs.get("iac_region")
    VERBOSE = metadata.inputs.get("verbose")

    inputs_list = [TF_STATE_BUCKET_NAME, TF_STATE_REGION, IAC_BUCKET_NAME, IAC_REGION]

    if None in inputs_list:
        print("- Some mandatory input is empty. Please, check the input list.")
        exit(1)

    with open(Path('manifest.yaml'), 'r') as file:
        manifesto_yaml = file.read()

    manifesto_dict = safe_load(manifesto_yaml)

    if VERBOSE is not None:
        print("- MANIFESTO:", manifesto_dict)

    manifestoType = manifesto_dict["manifesto"]["kind"]
    appOrInfraId = manifesto_dict["manifesto"]["spec"]["id"]

    print(f"{manifestoType} project identified, with ID: {appOrInfraId}")


    version_tag = manifesto_dict["versionTag"]
    if version_tag is None:
        print("- Version Tag not informed or couldn't be extracted.")
        exit(1) 
    
    is_api = manifesto_dict["isApi"]
    if is_api is None:
        print("- API TYPE not informed or couldn't be extracted.")
        exit(1) 
    
    envId = manifesto_dict["envId"]
    if envId is None:
        print("- ENVIRONMENT ID not informed or couldn't be extracted.")
        exit(1) 
    
    wksId = manifesto_dict["workspaceId"] 
    if wksId is None:
        print("- WORKSPACE ID not informed or couldn't be extracted.")
        exit(1) 

    branch = None
    if "runConfig" in manifesto_dict: 
        branch = manifesto_dict["runConfig"]["checkoutBranch"]
        print("Branch informed:", branch)
    
    api_contract_path = None
    if "apiContractPath" in manifesto_dict: 
        api_contract_path = manifesto_dict["apiContractPath"]
        print("API contract path informed:", api_contract_path)

    request_data = json.dumps(manifesto_dict)

    config_data = json.dumps(
        {
            "config": {
                "tfstate": {
                    "bucket": TF_STATE_BUCKET_NAME,
                    "region": TF_STATE_REGION
                },
                "iac": {
                    "bucket": IAC_BUCKET_NAME,
                    "region": IAC_REGION
                }
            }
        }
    )

    pipeline_url = {
        "pipelineUrl": "http://stackspot.com"
    }

    request_data = json.loads(request_data)
    request_data = {
        **request_data,
        **json.loads(config_data),
        **pipeline_url,
    }

    if branch is not None:
        branch_data = json.dumps(
            {
                "runConfig": {
                "branch": branch
                }
            }
        )
        request_data = {**request_data, **json.loads(branch_data)}

    if api_contract_path is not None:
        api_data = json.dumps(
            {
                "apiContractPath": api_contract_path
            }
        )
        request_data = {**request_data, **json.loads(api_data)}

    #request_data = json.dumps(request_data)

    if VERBOSE is not None:
        print("- DEPLOY RUN REQUEST DATA:", request_data)
    

    if manifestoType == 'application':
        manifest_type = 'app'
    elif manifestoType == 'shared-infrastructure':
        manifest_type = 'infra'
    else:
        print("- MANIFESTO TYPE not recognized. Please, check the input.")
        exit(1)

    print("Deploying Self-Hosted...")
    
    r2 = post_with_authorization(url=f"https://runtime-manager.stg.stackspot.com/v1/run/self-hosted/deploy/{manifest_type}", 
                                 body=request_data, 
                                 headers={'Content-Type': 'application/json' },
                                 timeout=20)
    

    if r2.status_code == 201:
        d2 = r2.json()
        runId = d2["runId"]
        runType = d2["runType"]
        tasks = d2["tasks"]

        save_output(d2)

        print(f"- RUN {runType} successfully started with ID: {runId}")
        print(f"- RUN TASKS LIST: {tasks}")

    else:
        print("- Error starting self hosted deploy run")
        print("- Status:", r2.status_code)
        print("- Error:", r2.reason)
        print("- Response:", r2.text)    
        exit(1)


