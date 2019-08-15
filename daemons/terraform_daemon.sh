#!/bin/bash

set -euo pipefail

if [[ $# != 1 ]]; then
    echo "Usage: $(basename $0) daemon-name"
    exit 1
fi

if [[ -z $DDS_DEPLOYMENT_STAGE ]]; then
    echo 'Please run "source environment" in the kharon repo root directory before running this command'
    exit 1
fi

daemon=$1

git clean -df $daemon/*.tf $daemon/.terraform

terraform_files=$(find $daemon -mindepth 1 -type f -name "*.tf" | sort --unique | wc -l)
if [[ $terraform_files == 0 ]]; then
    echo "Skipping terraform: no terraform files found for $daemon"
    exit 0
fi

echo "Terraforming $daemon"

./build_tf_deploy_config.py $daemon
(cd $daemon ; terraform init)
(cd $daemon ; TF_VAR_daemon=$daemon terraform apply -auto-approve)
