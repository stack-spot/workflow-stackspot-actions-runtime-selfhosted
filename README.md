# StackSpot actions runtimes repository

This repository contains various StackSpot Actions that can be used to automate processes in CI/CD pipelines. Additionally, there is a main action that orchestrates the execution of the other actions, simplifying the integration and management of multiple tasks in a single workflow.

## Repository Structure


## Requirements

Before using the actions in this repository, ensure that you have the following requirements:

* StackSpot CLI installed and configured.

## How to Use

### Deploy

```bash
stk run action <path-where-u-cloned-the-repository> \
    --workflow_type deploy \
    --environment "<environment>" \
    --version_tag "<version-tag>" \
    --repository_name "<repository-name>" \
    --client_id "<stackspot-client-id>" \
    --client_key "<stackspot-client-key>" \
    --client_realm "<stackspot-client-realm>" \
    --aws_access_key_id "<aws-access-key-id>" \
    --aws_secret_access_key "<aws-secret-access-key>" \
    --aws_session_token "<aws-session-token>" \
    --tf_state_bucket_name "<tf_state_bucket>" \
    --iac_bucket_name "<iac_bucket_name>" \
    --tf_state_region "<aws-region>" \
    --iac_region "<aws-region>" \
    --aws_region "<aws-region>"
```

### Cancel

```bash
stk run action <path-where-u-cloned-the-repository> \
    --workflow_type cancel \
    --run_id "<run_id>"
```