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

echo "Running pre-packaging steps for $daemon"

git clean -df $daemon/domovoilib $daemon/vendor


cp -R ../dds $daemon/domovoilib
aws secretsmanager get-secret-value --secret-id ${DDS_SECRETS_STORE}/${DDS_DEPLOYMENT_STAGE}/gcp-credentials.json \
    | jq -r .SecretString > $daemon/domovoilib/gcp-credentials.json
