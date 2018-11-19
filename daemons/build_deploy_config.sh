#!/bin/bash

set -euo pipefail

if [[ $# != 1 ]]; then
    echo "Usage: $(basename $0) daemon-name"
    exit 1
fi

if [[ -z $DDS_DEPLOYMENT_STAGE ]]; then
    echo 'Please run "source environment" in the data-store repo root directory before running this command'
    exit 1
fi

export daemon_name=$1
export stage=$DDS_DEPLOYMENT_STAGE
config_json="$(dirname $0)/${daemon_name}/.chalice/config.json"

export iam_role_arn=$(cd $daemon_name ; terraform output role-arn)
cat "$config_json" | jq .manage_iam_role=false | jq .iam_role_arn=env.iam_role_arn | sponge "$config_json"

export DSS_ES_ENDPOINT=$(aws es describe-elasticsearch-domain --domain-name "$DSS_ES_DOMAIN" | jq -r .DomainStatus.Endpoint)

for var in $EXPORT_ENV_VARS_TO_LAMBDA DSS_ES_ENDPOINT; do
    cat "$config_json" | jq .stages.$stage.environment_variables.$var=env.$var | sponge "$config_json"
done
