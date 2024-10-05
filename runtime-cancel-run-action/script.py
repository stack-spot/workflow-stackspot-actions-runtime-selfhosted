import os
from oscli.core.http import post_with_authorization


STK_RUNTIME_MANAGER_DOMAIN = os.getenv("STK_RUNTIME_MANAGER_DOMAIN", "https://runtime-manager.v1.stackspot.com")


def run(metadata):
    """
    Cancels a running process identified by the provided RUN_ID.

    This function sends a cancellation request to the StackSpot Runtime Manager API
    to cancel a running process. The cancellation is forced by appending `?force=true`
    to the request URL.

    Parameters:
    -----------
    metadata : object
        An object containing the inputs for the function. It must include a 'run_id' key
        in the `inputs` dictionary, which holds the ULID of the run to be cancelled.

    Example:
    --------
    metadata = {
        'inputs': {
            'run_id': '01F8MECHZX3TBDSZ7XRADM79XE'
        }
    }
    run(metadata)

    The function will print the status of the cancellation request based on the response
    from the API.

    API Response Status Codes:
    --------------------------
    - 202: The run was successfully cancelled.
    - 404: The run was not found.
    - 422: The run is not currently running, so it cannot be aborted.
    - Other: Any other status code will be treated as an error, and the function will
      print the error details and exit the program.

    """
    
    # Extract the RUN_ID from the metadata inputs
    RUN_ID = metadata.inputs['run_id']
    print(f"> Requesting Run {RUN_ID} to be cancelled")
    
    # Send a POST request to cancel the run
    cancel_request = post_with_authorization(
        url=f"{STK_RUNTIME_MANAGER_DOMAIN}/v1/run/cancel/{RUN_ID}?force=true", 
        headers={'Content-Type': 'application/json'},
        body=None,
        timeout=20
    )

    # Handle the response based on the status code
    if cancel_request.status_code == 202:
        print(f"> Cancelled successfully!")
    elif cancel_request.status_code == 404:
        print(f"> Not found.")
    elif cancel_request.status_code == 422:
        print(f"> Not currently running. Unable to Abort.")
    else:
        # Handle any other error response
        print("- Error cancelling run")
        print("- Status:", cancel_request.status_code)
        print("- Error:", cancel_request.reason)
        print("- Response:", cancel_request.text)
        exit(1)