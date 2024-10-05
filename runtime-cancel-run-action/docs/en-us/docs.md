## runtime-cancel-run-action

Cancel Running Process

This action cancels a running process identified by a `RUN_ID` by sending a cancellation request to the StackSpot Runtime Manager API.

## Requirements

- The user must have access to the StackSpot Runtime Manager API.
- The `run_id` of the process to be cancelled must be provided.

## Usage

1. Input:
   - `run_id`: The ULID of the process to be cancelled.
   
2. Example usage:
   stk run action . --run_id 01J9EKHN5V2R75MGGT8KMEAGH1