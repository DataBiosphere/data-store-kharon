#!/bin/bash

set -euo pipefail

if [[ $# != 3 ]]; then
    echo "Usage: $(basename $0) daemon-name stage lambda-input-file"
    exit 1
fi

lambda_name="$1-$2"
lambda_input_file=$3

sqs_arn="arn:aws:sqs:${AWS_DEFAULT_REGION}:$(aws sts get-caller-identity | jq -r .Account):${lambda_name}"
lambda_input=$(cat ${lambda_input_file} | jq -r --arg arn ${sqs_arn} '.Records[0].eventSourceARN = $arn')

raw_lambda_output="$(aws lambda invoke --function-name $lambda_name --invocation-type RequestResponse --payload "${lambda_input}" --log-type Tail /dev/stdout)"
lambda_output="$(echo $raw_lambda_output | jq -r '. | select(.LogResult)')"

# lambda output is occasionally malformed as appended JSON objects: {"wrong_obj": ... }{"LogResult": ...}
# This selects the object we wish to examine for error
echo "$lambda_output" | jq -r .LogResult | base64 --decode

[[ $(echo "$lambda_output" | jq -r .FunctionError) == null ]]
