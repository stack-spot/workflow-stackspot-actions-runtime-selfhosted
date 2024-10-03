from pathlib import Path
import subprocess
import json
from sys import exit

def check(result):
    if (result.returncode == 1):
        print(f"Fail to execute {result.args[:100]}...") 
        exit(1)


def run(metadata):

    manifest_action = f'{metadata.inputs.get("base_path_actions")}/runtime-create-manifest-action'
    manager_action = f'{metadata.inputs.get("base_path_actions")}/runtime-manager-action'
    iac_action = f'{metadata.inputs.get("base_path_actions")}/runtime-iac-action'
    container_url_iac = 'stackspot/runtime-job-iac:rc-2.19.0'
    deploy_action = f'{metadata.inputs.get("base_path_actions")}/runtime-deploy-action'
    container_url_deploy = 'stackspot/runtime-job-deploy:rc-2.36.0'

    print(f"-----> Run runtime-create-manifest-action!")

    result = subprocess.run([metadata.inputs.get('stk'), 'run', 'action', manifest_action, '--environment', metadata.inputs.get('environment'), '--workspace', metadata.inputs.get('workspace'), '--version_tag', metadata.inputs.get('version_tag'), '--branch', metadata.inputs.get('branch'), '--dynamic_inputs', metadata.inputs.get('dynamic_inputs'), '--verbose', f"{metadata.inputs.get('verbose')}", '--stk',  metadata.inputs.get('stk'), '--non-interactive'])

    check(result)

    print(f"-----> Run runtime-manager-action!")

    result = subprocess.run([metadata.inputs.get('stk'), 'run', 'action', manager_action , '--tf_state_bucket_name', metadata.inputs.get('tf_state_bucket_name'),  '--tf_state_region', metadata.inputs.get('tf_state_region'), '--iac_bucket_name', metadata.inputs.get('iac_bucket_name'), '--iac_region', metadata.inputs.get('iac_region') , '--verbose', f"{metadata.inputs.get('verbose')}", '--workdir', metadata.inputs.get('workdir'), '--non-interactive'])

    check(result)

    with open('manager-output.log', 'r') as file:
        data = json.loads(file.read().replace("\'", "\""))

    for t in data['tasks']:
        if t["taskType"] == "IAC_SELF_HOSTED":
  
            print(f"-----> Run runtime-iac-action!")
            
            result = subprocess.run([metadata.inputs.get('stk'), 'run', 'action', iac_action, '--features_level_log', metadata.inputs.get('features_level_log'), '--client_id',  metadata.inputs.get('client_id'), '--client_key', metadata.inputs.get('client_key'), '--client_realm', metadata.inputs.get('client_realm'), '--repository_name',  metadata.inputs.get('repository_name'), '--aws_access_key_id', metadata.inputs.get('aws_access_key_id'), '--aws_secret_access_key', metadata.inputs.get('aws_secret_access_key'), '--aws_session_token', metadata.inputs.get('aws_session_token'), '--aws_region', metadata.inputs.get('aws_region'), '--run_task_id', t["runTaskId"], '--path_to_mount', metadata.inputs.get('path_to_mount'), '--base_path_output',  metadata.inputs.get('base_path_output'), '--container_url',  container_url_iac, '--non-interactive'])
            
            check(result)


        elif t["taskType"] == "DEPLOY_SELF_HOSTED":
            print(f"-----> Run runtime-deploy-action!")

            result = subprocess.run([metadata.inputs.get('stk'), 'run', 'action', deploy_action, '--features_level_log',  metadata.inputs.get('features_level_log'), '--client_id',  metadata.inputs.get('client_id'), '--client_key',  metadata.inputs.get('client_key'), '--client_realm',  metadata.inputs.get('client_realm'), '--repository_name',  metadata.inputs.get('repository_name'), '--aws_access_key_id',  metadata.inputs.get('aws_access_key_id'), '--aws_secret_access_key',  metadata.inputs.get('aws_secret_access_key'), '--aws_session_token',  metadata.inputs.get('aws_session_token'), '--aws_region',  metadata.inputs.get('aws_region'), '--run_task_id', t['runTaskId'], '--container_url', container_url_deploy, '--features_terraform_modules',  metadata.inputs.get('features_terraform_modules'), '--path_to_mount',  metadata.inputs.get('path_to_mount'), '--output_file', 'deploy-output.json', '--localexec_enabled', f"{metadata.inputs.get('localexec_enabled')}", '--tf_log_provider',  metadata.inputs.get('tf_log_provider'), '--non-interactive'])

            check(result)
        else:
            print(f"-----> Unsupported task type {t['taskType']}")
