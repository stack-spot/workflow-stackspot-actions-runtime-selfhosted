from pathlib import Path
import subprocess
import json
from sys import exit

def check(result):
    if (result.returncode == 1):
        print(f"Fail to execute {result.args[:100]}...") 
        exit(1)

class RunAction:
    def __init__(self, metadata):
        self.stk = metadata.inputs.get('stk') or "stk"
        self.action_base_path = metadata.inputs["base_path_actions"]
        self.inputs = {k: v for k, v in metadata.inputs.items() if v is not None}

    def __run__(self, action_name: str, **inputs):
        print(f"Running: {action_name}")
        action_path = f'{self.action_base_path}/{action_name}'
        cmd =  [self.stk, 'run', 'action', action_path, '--inputs-json', json.dumps({**self.inputs, **inputs}),'--non-interactive']
        result = subprocess.run(cmd)
        check(result)


def run(metadata):
    run_action = RunAction(metadata)
    run_action("runtime-create-manifest-action")
    run_action("runtime-manager-action")

    with open('manager-output.log', 'r') as file:
        data = json.loads(file.read().replace("\'", "\""))
    
    for t in data['tasks']:
        inputs = dict(run_task_id=t["runTaskId"])
        t["taskType"] == "IAC_SELF_HOSTED" and run_action("", container_url=container_url_iac, **inputs)
        t["taskType"] == "DEPLOY_SELF_HOSTED" and run_action("", container_url=container_url_deploy, output_file="deploy-output.json", **inputs)
