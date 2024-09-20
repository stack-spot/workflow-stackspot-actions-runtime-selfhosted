from oscli.core.http import post_with_authorization

def run(metadata):

    RUN_ID = metadata.inputs.get('run_id')
    FORCE = metadata.inputs.get('force_cancel')

    print(FORCE)
        
    if RUN_ID == "":
        print("- RUN_ID was not provided.")
        print("  No need to cancel it.")
        exit(0)

    # Calling Cancel Action
    print("Cancelling Run...")

    print(f"Requesting Run {RUN_ID} to be cancelled")

    cancel_request = post_with_authorization(url=f"https://runtime-manager.stg.stackspot.com/v1/run/cancel/{RUN_ID}?force={FORCE}", 
                                    headers={'Content-Type': 'application/json' },
                                    body=None,
                                    timeout=20)
        
    if cancel_request.status_code == 202:
        print(f"- RUN {RUN_ID} cancelled successfully!")

    elif cancel_request.status_code == 404:
        print(f"- RUN {RUN_ID} not found.")

    elif cancel_request.status_code == 422:
        print(f"- RUN {RUN_ID} not currently running. Unable to Abort.")

    else:
        print("- Error cancelling run")
        print("- Status:", cancel_request.status_code)
        print("- Error:", cancel_request.reason)
        print("- Response:", cancel_request.text)
        exit(1)

