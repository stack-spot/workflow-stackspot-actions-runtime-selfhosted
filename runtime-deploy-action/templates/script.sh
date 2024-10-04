FLAGS=$(echo "-v {{ inputs.path_to_mount }}:/app-volume  \
-e FEATURES_LEVEL_LOG={{ inputs.features_level_log }} \
-e AUTHENTICATE_CLIENT_ID={{ inputs.client_id }} \
-e AUTHENTICATE_CLIENT_SECRET={{ inputs.client_key }} \
-e AUTHENTICATE_CLIENT_REALMS={{ inputs.client_realm }} \
-e AUTHENTICATE_URL=https://idm.stackspot.com \
-e REPOSITORY_NAME={{ inputs.repository_name }} \
-e FEATURES_API_MANAGER=https://runtime-manager.v1.stackspot.com \
-e FEATURES_BASEPATH_TMP=/tmp/runtime/deploys \
-e FEATURES_BASEPATH_EBS=/opt/runtime \
-e FEATURES_TEMPLATES_FILEPATH=/app/ \
-e FEATURES_BASEPATH_TERRAFORM=/root/.asdf/shims/terraform \
-e AWS_REGION={{ inputs.aws_region }} \
-e FEATURES_RELEASE_LOCALEXEC={{ inputs.localexec_enabled }}")

if [ -z "{{ inputs.aws_role_arn }}" ]; then
    FLAGS=$(echo "$FLAGS -e AWS_ACCESS_KEY_ID={{ inputs.aws_access_key_id }}")
    FLAGS=$(echo "$FLAGS -e AWS_SECRET_ACCESS_KEY={{ inputs.aws_secret_access_key }}")
    FLAGS=$(echo "$FLAGS -e AWS_SESSION_TOKEN={{ inputs.aws_session_token }}")
fi


if [ ! -z "{{ inputs.tf_log_provider }}" ]; then
    FLAGS=$(echo "$FLAGS -e FEATURES_TERRAFORM_LOGPROVIDER={{ inputs.tf_log_provider }}")
fi


docker run --rm \
$FLAGS \
-e FEATURES_TERRAFORM_MODULES='{{ inputs.features_terraform_modules }}' \
--entrypoint=/app/stackspot-runtime-job-deploy \
{{ inputs.container_url }} start --run-task-id="{{ inputs.run_task_id }}" --output-file="{{ inputs.output_file }}"