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
export daemon_tag=$(echo $daemon_name | cut -d '-' -f2-)
export stage=$DDS_DEPLOYMENT_STAGE
config_json="$(dirname $0)/${daemon_name}/.chalice/config.json"

export iam_role_arn=$(cd $daemon_name ; terraform output role-arn)
cat "$config_json" | jq .manage_iam_role=false | jq .iam_role_arn=env.iam_role_arn | sponge "$config_json"


export layer_name=dds-dependencies-${stage}
export layer_version_arn=$(aws lambda list-layers | jq -r '.Layers[] | select(.LayerName == env.layer_name) | .LatestMatchingVersion.LayerVersionArn')
cat "$config_json" | jq ".stages.$stage.layers=[env.layer_version_arn]" | sponge "$config_json"

data_store_env=$(aws ssm get-parameter --name /dcp/dss/${DDS_DEPLOYMENT_STAGE}/environment | jq -r .Parameter.Value | jq .)
export DSS_ES_ENDPOINT=$(echo $data_store_env | jq -r .DSS_ES_ENDPOINT)


export DEPLOY_ORIGIN="$(whoami)-$(hostname)-$(git describe --tags --always)-$(date -u +'%Y-%m-%d-%H-%M-%S').deploy"
cat "$config_json" | jq ".stages.$stage.tags.DSS_DEPLOY_ORIGIN=\"$DEPLOY_ORIGIN\" | \
	.stages.$stage.tags.Name=\"${DDS_INFRA_TAG_SERVICE}-$daemon_tag\" | \
	.stages.$stage.tags.service=\"${DDS_INFRA_TAG_SERVICE}\"  | \
	.stages.$stage.tags.project=\"$DDS_INFRA_TAG_PROJECT\" | \
	.stages.$stage.tags.owner=\"${DDS_INFRA_TAG_OWNER}\" | \
	.stages.$stage.tags.env=\"${DDS_DEPLOYMENT_STAGE}\""  | sponge "$config_json"

for var in $EXPORT_ENV_VARS_TO_LAMBDA DSS_ES_ENDPOINT; do
    cat "$config_json" | jq .stages.$stage.environment_variables.$var=env.$var | sponge "$config_json"
done

for var in DSS_S3_BUCKET DSS_GS_BUCKET; do
    val=$(echo $data_store_env | jq .$var)
    cat "$config_json" | jq .stages.$stage.environment_variables.$var="$val" | sponge "$config_json"
done
