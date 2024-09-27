$HOME/.{{ inputs.stk }}/bin/{{ inputs.stk }} use workspace {{ inputs.workspace }}

FLAGS=$(echo "--env {{ inputs.environment }} --version {{ inputs.version_tag }}")

if [ ! -z "{{ inputs.branch }}" ]; then
  FLAGS=$(echo "$FLAGS --branch {{ inputs.branch }}")
fi

if [ ! -z "{{ inputs.open_api_path }}" ]; then
  FLAGS=$(echo "$FLAGS --open-api-path {{ inputs.open_api_path }}")
fi

if [ ! -z "{{ inputs.dynamic_inputs }}" ]; then
  FLAGS=$(echo "$FLAGS {{ inputs.dynamic_inputs }}")
fi

if [ ! -z "{{ inputs.verbose }}" ]; then
  echo "$HOME/.{{ inputs.stk }}/bin/{{ inputs.stk }} deploy plan FLAGS = $FLAGS"
fi

$HOME/.{{ inputs.stk }}/bin/{{ inputs.stk }} deploy plan $FLAGS