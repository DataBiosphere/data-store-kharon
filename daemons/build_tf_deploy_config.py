#!/usr/bin/env python
"""
This script generates Terraform scripting needed for daemons that deploy infrastructure.
"""

import os
import glob
import json
import boto3
import argparse
from google.cloud.storage import Client


daemons_root = os.path.abspath(os.path.dirname(__file__))


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("daemon")
args = parser.parse_args()


env_vars_to_lambda = os.environ['EXPORT_ENV_VARS_TO_LAMBDA'].split()
stage=os.environ['DDS_DEPLOYMENT_STAGE']


terraform_backend_template = """# Auto-generated
# Please edit daemons/build_tf_deploy_config.py
terraform {{
  backend "s3" {{
    bucket = "{bucket}"
    key = "dds/dds-{daemon}-{stage}.tfstate"
    region = "{region}"
    {profile_setting}
  }}
}}
"""

terraform_providers_template = """# Auto-generated
# Please edit infra/build_tf_deploy_config.py
provider aws {{
  region = "{aws_region}"
}}

provider google {{
  project = "{gcp_project_id}"
}}
"""

account_id = boto3.client("sts").get_caller_identity()['Account']
backend_bucket = os.environ['DDS_TERRAFORM_BACKEND_BUCKET_TEMPLATE'].format(account_id=account_id)

terraform_variable_info = {'variable': {'account_id': {'default': account_id}}}
for key in env_vars_to_lambda:
    terraform_variable_info['variable'][key] = {
        'default': os.environ[key]
    }
parm = boto3.client("ssm").get_parameter(Name=f"/dcp/dss/{stage}/environment")
dss_lambda_env_vars = json.loads(parm['Parameter']['Value'])
for key, val in dss_lambda_env_vars.items():
    terraform_variable_info['variable'][key] = dict(default=val)

with open(os.path.join(daemons_root, args.daemon, "backend.tf"), "w") as fp:
    if os.environ.get('AWS_PROFILE'):
        profile = os.environ['AWS_PROFILE']
        profile_setting = f'profile = "{profile}"'
    else:
        profile_setting = ''
    fp.write(terraform_backend_template.format(
        bucket=backend_bucket,
        daemon=args.daemon,
        stage=stage,
        region=os.environ['AWS_DEFAULT_REGION'],
        profile_setting=profile_setting,
    ))

with open(os.path.join(daemons_root, args.daemon, "variables.tf"), "w") as fp:
    fp.write(json.dumps(terraform_variable_info, indent=2))

with open(os.path.join(daemons_root, args.daemon, "providers.tf"), "w") as fp:
    fp.write(terraform_providers_template.format(
        aws_region=os.environ['AWS_DEFAULT_REGION'],
        gcp_project_id=Client().project,
    ))
