FLAGS=$(echo "-v {{ inputs.path_to_mount }}:/app-volume  \
-e FEATURES_LEVEL_LOG={{ inputs.features_level_log }} \
-e AUTHENTICATE_CLIENT_ID={{ inputs.client_id }} \
-e AUTHENTICATE_CLIENT_SECRET={{ inputs.client_key }} \
-e AUTHENTICATE_CLIENT_REALMS={{ inputs.client_realm }} \
-e AUTHENTICATE_URL="https://idm.stackspot.com" \
-e FEATURES_API_MANAGER="https://runtime-manager.v1.stackspot.com" \
-e REPOSITORY_NAME={{ inputs.repository_name }} \
-e AWS_REGION={{ inputs.aws_region }}")

if [ -z "{{ inputs.AWS_ROLE_ARN }}" ]; then
    FLAGS=$(echo "$FLAGS -e AWS_ACCESS_KEY_ID={{ inputs.aws_access_key_id }}")
    FLAGS=$(echo "$FLAGS -e AWS_SECRET_ACCESS_KEY={{ inputs.aws_secret_access_key }}")
    FLAGS=$(echo "$FLAGS -e AWS_SESSION_TOKEN={{ inputs.aws_session_token }}")
fi


docker run --rm \
$FLAGS \
--entrypoint=/app/stackspot-runtime-job-iac \
{{ inputs.container_url }} start --run-task-id="{{ inputs.run_task_id }}" --base-path-output="{{ inputs.base_path_output }}"