import os
import sys
import subprocess
import logging
from typing import List

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


STK_IAM_DOMAIN = os.getenv("STK_IAM_DOMAIN", "https://idm.stackspot.com")
STK_RUNTIME_MANAGER_DOMAIN = os.getenv(
    "STK_RUNTIME_MANAGER_DOMAIN", "https://runtime-manager.v1.stackspot.com"
)
CONTAINER_UNIFIED_URL = os.getenv(
    "CONTAINER_UNIFIED_URL", "stackspot/runtime-job-unified:latest"
)

FEATURES_BASEPATH_TMP = "/tmp/runtime/deploys"
FEATURES_BASEPATH_EBS = "/opt/runtime"
FEATURES_TEMPLATES_FILEPATH = "/app/"
FEATURES_BASEPATH_TERRAFORM = "/root/.asdf/shims/terraform"


def check(result: subprocess.Popen) -> None:
    """
    Checks the result of a subprocess execution. If the return code is non-zero,
    it logs an error message and exits the program.

    Args:
        result (subprocess.Popen): The result of the subprocess execution.
    """
    result.wait()  # Wait for the process to complete
    if result.returncode != 0:
        logging.error(f"Failed to execute: {result.args}")
        logging.error(f"Error output: {result.stderr.read()}")
        sys.exit(1)


def run_command(command: List[str]) -> subprocess.Popen:
    """
    Runs a command using subprocess.Popen and returns the result.

    Args:
        command (List[str]): The command to be executed as a list of strings.

    Returns:
        subprocess.Popen: The result of the command execution.
    """
    try:
        logging.info(f"Running command: {' '.join(command)}")
        # Start the process
        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        # Read and print output in real-time
        for line in process.stdout:
            print(line, end="")  # Print each line as it is produced

        # Check the result after the process completes
        check(process)
        return process
    except Exception as e:
        logging.error(f"Exception occurred while running command: {command}")
        logging.error(str(e))
        sys.exit(1)


def build_flags(inputs: dict) -> list:

    TF_PARALLELISM = f"-parallelism={inputs.get('tf_parallelism') or '10'}"

    docker_flags: dict = dict(
        FEATURES_LEVEL_LOG=inputs.get("features_level_log") or "info",
        FEATURES_TERRAFORM_LOGPROVIDER=inputs.get("tf_log_provider") or "info",
        FEATURES_RELEASE_LOCALEXEC=inputs.get("localexec_enabled") or "False",
        FEATURES_TERRAFORM_MODULES=inputs.get("features_terraform_modules") or "[]",
        AWS_ACCESS_KEY_ID=inputs["aws_access_key_id"],
        AWS_SECRET_ACCESS_KEY=inputs["aws_secret_access_key"],
        AWS_SESSION_TOKEN=inputs["aws_session_token"],
        AUTHENTICATE_CLIENT_ID=inputs["client_id"],
        AUTHENTICATE_CLIENT_SECRET=inputs["client_key"],
        AUTHENTICATE_CLIENT_REALMS=inputs["client_realm"],
        REPOSITORY_NAME=inputs["repository_name"],
        AWS_REGION=inputs["aws_region"],
        AUTHENTICATE_URL=STK_IAM_DOMAIN,
        FEATURES_API_MANAGER=STK_RUNTIME_MANAGER_DOMAIN,
        FEATURES_BASEPATH_TMP=FEATURES_BASEPATH_TMP,
        FEATURES_BASEPATH_EBS=FEATURES_BASEPATH_EBS,
        FEATURES_TEMPLATES_FILEPATH=FEATURES_TEMPLATES_FILEPATH,
        FEATURES_BASEPATH_TERRAFORM=FEATURES_BASEPATH_TERRAFORM,
        TF_CLI_ARGS_apply=TF_PARALLELISM,
        TF_CLI_ARGS_plan=TF_PARALLELISM,
        TF_CLI_ARGS_destroy=TF_PARALLELISM,
    )
    flags = []
    for k, v in docker_flags.items():
        flags += ["-e", f"{k}={v}"]

    return flags


def run(metadata):
    inputs: dict = metadata.inputs
    run_id: str = inputs["run_id"]
    base_path_output: str = inputs.get("base_path_output") or "."
    path_to_mount: str = inputs.get("path_to_mount") or "."
    path_to_mount = f"{path_to_mount}:/app-volume"

    flags = build_flags(inputs)
    cmd = (
        ["docker", "run", "--rm", "-v", path_to_mount]
        + flags
        + [
            "--entrypoint=/app/stackspot-runtime-job",
            CONTAINER_UNIFIED_URL,
            "start",
            f"--run-id={run_id}",
            f"--base-path-output={base_path_output}",
        ]
    )

    run_command(cmd)
