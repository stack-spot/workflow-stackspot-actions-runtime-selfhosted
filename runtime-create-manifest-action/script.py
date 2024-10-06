import sys
import subprocess
import logging
from typing import List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


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
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
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

    
def run(metadata) -> None:
    """
    Executes a cmd of StackSpot CLI to deploy a plan.

    Args:
        metadata (object): An object containing the inputs required for the execution.
    """
    stk = sys.argv[0]
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
    stk_deploy_plan = [stk, "deploy", "plan", "--env", environment, "--version", version_tag] + optional_params

    # Execute the commands
    run_command(stk_deploy_plan)