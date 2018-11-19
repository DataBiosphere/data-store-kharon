#!/usr/bin/env python3

import os
import glob
import json
import boto3
import argparse
from google.cloud.storage import Client
GCP_PROJECT_ID = Client().project


infra_root = os.path.abspath(os.path.dirname(__file__))


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("component")
args = parser.parse_args()


terraform_backend_template = """# Auto-generated during infra build process.
# Please edit infra/build_deploy_config.py directly.
terraform {{
  backend "s3" {{
    bucket = "{bucket}"
    key = "dds/{comp}-{stage}.tfstate"
    region = "{region}"
    {profile_setting}
  }}
}}
"""

terraform_providers_template = """# Auto-generated during infra build process.
# Please edit infra/build_deploy_config.py directly.
provider aws {{
  region = "{aws_region}"
}}

provider google {{
  project = "{gcp_project_id}"
}}
"""

env_vars_to_infra = [
    "AWS_DEFAULT_REGION",
    "DDS_DEPLOYMENT_STAGE",
    "DDS_GCP_SERVICE_ACCOUNT_NAME",
]

account_id = boto3.client("sts").get_caller_identity()['Account']
backend_bucket = os.environ['DDS_TERRAFORM_BACKEND_BUCKET_TEMPLATE'].format(account_id=account_id)

terraform_variable_info = {'variable': dict()}
for key in env_vars_to_infra:
    terraform_variable_info['variable'][key] = {
        'default': os.environ[key]
    }

with open(os.path.join(infra_root, args.component, "backend.tf"), "w") as fp:
    if os.environ.get('AWS_PROFILE'):
        profile = os.environ['AWS_PROFILE']
        profile_setting = f'profile = "{profile}"'
    else:
        profile_setting = ''
    fp.write(terraform_backend_template.format(
        bucket=backend_bucket,
        comp=args.component,
        stage=os.environ['DDS_DEPLOYMENT_STAGE'],
        region=os.environ['AWS_DEFAULT_REGION'],
        profile_setting=profile_setting,
    ))

with open(os.path.join(infra_root, args.component, "variables.tf"), "w") as fp:
    fp.write(json.dumps(terraform_variable_info, indent=2))

with open(os.path.join(infra_root, args.component, "providers.tf"), "w") as fp:
    fp.write(terraform_providers_template.format(
        aws_region=os.environ['AWS_DEFAULT_REGION'],
        gcp_project_id=GCP_PROJECT_ID,
    ))
