import os
import sys
from pathlib import Path
import subprocess
import json
from sys import exit


class RunAction:
    def __init__(self, metadata):
        self.stk = sys.argv[0]
        self.action_base_path = os.path.dirname(os.path.abspath(__file__))
        self.inputs = {k: v for k, v in metadata.inputs.items() if v is not None}

    def __call__(self, action_name: str, **inputs):
        action_path = f"{self.action_base_path}/{action_name}"
        cmd = [
            self.stk,
            "run",
            "action",
            action_path,
            "--inputs-json",
            json.dumps({**self.inputs, **inputs}),
            "--non-interactive",
        ]
        result = subprocess.run(cmd)
        if result.returncode == 1:
            print(f"Fail to execute {result.args}...")
            exit(1)


def deploy_workflow(run_action: RunAction):
    run_action("runtime-create-manifest-action")
    run_action("runtime-manager-action")

    run_tasks("manager-output.log", run_action)


def cancel_deploy_run(run_action: RunAction):
    run_action("runtime-cancel-run-action")


def rollback_deploy_run(run_action: RunAction):
    run_action("runtime-rollback-action")
    run_tasks("rollback-output.log", run_action)


def run_tasks(file_tasks: str, run_action: RunAction):
    with open(file_tasks, "r") as file:
        data = json.loads(file.read().replace("'", '"'))

    task_runners = dict(
        IAC_SELF_HOSTED=lambda **i: run_action("runtime-iac-action", **i),
        DEPLOY_SELF_HOSTED=lambda **i: run_action("runtime-deploy-action", **i),
        DESTROY_SELF_HOSTED=lambda **i: run_action("runtime-destroy-action", **i),
        PLAN=lambda **i: run_action("runtime-unified-action", **i),
        UNIFIED_IAC=lambda **i: run_action("runtime-unified-action", **i),
        UNIFIED_DEPLOY=lambda **i: run_action("runtime-unified-action", **i),
        UNIFIED_DESTROY=lambda **i: run_action("runtime-unified-action", **i),
    )

    for t in data.get("tasks") or []:
        task_type = t["taskType"]
        runner = task_runners.get(task_type)
        if "UNIFIED" in task_type:
            runner and runner(run_id=data.get("runId"))
        elif "PLAN" == task_type:
            runner and runner(run_id=data.get("runId"))
        else:
            runner and runner(run_task_id=t["runTaskId"])


def run(metadata):
    workflows = dict(
        deploy=deploy_workflow,
        cancel=cancel_deploy_run,
        rollback_deploy=rollback_deploy_run,
    )
    run_action = RunAction(metadata)
    workflow_runner = workflows.get(metadata.inputs["workflow_type"])
    workflow_runner and workflow_runner(run_action=run_action)
