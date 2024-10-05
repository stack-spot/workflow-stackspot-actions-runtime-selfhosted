import sys
import subprocess
import logging
from typing import List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

def run(metadata) -> None:
    """
    Executes a series of StackSpot CLI commands to set the workspace and deploy a plan.

    Args:
        metadata (object): An object containing the inputs required for the execution.
    """
    stk = sys.argv[0]
    workspace = metadata.inputs['workspace']
    environment = metadata.inputs['environment']
    version_tag = metadata.inputs['version_tag']
    open_api_path: Optional[str] = metadata.inputs.get('open_api_path')
    dynamic_inputs: Optional[str] = metadata.inputs.get('dynamic_inputs')

    # Prepare optional parameters for the deploy command
    optional_params = []
    if open_api_path:
        optional_params += ["--open-api-path", open_api_path]
    if dynamic_inputs:
        optional_params += dynamic_inputs.split()

    # Prepare the StackSpot CLI commands
    stk_use_workspace = [stk, "use", "workspace", workspace]
    stk_deploy_plan = [stk, "deploy", "plan", "--env", environment, "--version", version_tag] + optional_params

    # Execute the commands
    run_command(stk_use_workspace)
    run_command(stk_deploy_plan)