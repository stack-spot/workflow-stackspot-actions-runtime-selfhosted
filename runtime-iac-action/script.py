import os
import sys
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


STK_IAM_DOMAIN = os.getenv("STK_IAM_DOMAIN", "https://idm.stackspot.com")
STK_RUNTIME_MANAGER_DOMAIN = os.getenv("STK_RUNTIME_MANAGER_DOMAIN", "https://runtime-manager.v1.stackspot.com")


def check(result: subprocess.CompletedProcess) -> None:
    """
    Checks the result of a subprocess execution. If the return code is non-zero, 
    it logs an error message and exits the program.

    Args:
        result (subprocess.CompletedProcess): The result of the subprocess execution.
    """
    if result.returncode != 0:
        logging.error(f"Failed to execute: {result.args}")
        logging.error(f"Error output: {result.stderr}")
        sys.exit(1)

def run_command(command: List[str]) -> subprocess.CompletedProcess:
    """
    Runs a command using subprocess and returns the result.

    Args:
        command (List[str]): The command to be executed as a list of strings.

    Returns:
        subprocess.CompletedProcess: The result of the command execution.
    """
    try:
        logging.info(f"Running command: {' '.join(command)}")
        result = subprocess.run(command, capture_output=True, text=True)
        check(result)
        return result
    except Exception as e:
        logging.error(f"Exception occurred while running command: {command}")
        logging.error(str(e))
        sys.exit(1)



def run(metadata):
    inputs: dict = metadata.inputs
    container_url: str = 'stackspot/runtime-job-iac:latest'
    run_task_id: str = inputs["run_task_id"]
    base_path_output: str = inputs.get("base_path_output") or "."
    path_to_mount: str = inputs.get("path_to_mount") or "."
    path_to_mount = f"{path_to_mount}:/app-volume" 

    docker_flags: dict = dict(
        FEATURES_LEVEL_LOG=inputs.get("features_level_log") or "info",
        
        AUTHENTICATE_CLIENT_ID=inputs["client_id"],
        AUTHENTICATE_CLIENT_SECRET=inputs["client_key"],
        AUTHENTICATE_CLIENT_REALMS=inputs["client_realm"],
        REPOSITORY_NAME=inputs["repository_name"],
        AWS_REGION=inputs["aws_region"],

        AUTHENTICATE_URL=STK_IAM_DOMAIN,
        FEATURES_API_MANAGER=STK_RUNTIME_MANAGER_DOMAIN,
    )

    cmd = [
        "docker", 
        "run", "--rm",
        "--entrypoint=/app/stackspot-runtime-job-iac",
        container_url, 
        "start",
        f"--run-task-id={run_task_id}", 
        f"--base-path-output={base_path_output}", 
        "-v", path_to_mount
    ]
    flags = []
    for k, v in docker_flags.items():
        flags += ["-e", f"{k}={v}"]
    docker_run = cmd + flags

    run_command(docker_run)
