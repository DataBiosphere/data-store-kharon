# HCA Kharon: The Human Cell Atlas Data Deletion System

This repository contains AWS infrastructure definitions and procedures to carry out data deletions in the
[Data Storage System](https://github.com/HumanCellAtlas/data-store).

## Installing dependencies

1. Install `terraform` by following the instructions in
[Install Terraform](https://www.terraform.io/intro/getting-started/install.html)

## Environment Variables

Environment variables are required for test and deployment. The required environment variables and their default values
are in the file `environment`. To customize the values of these environment variables:

1. Copy `environment.local.example` to `environment.local`
1. Edit `environment.local` to add custom entries that override the default values in `environment`
    
Run `source environment` now and whenever these environment files are modified.

## Deployment

1. Deploy the GCP service account with `make gcp-service-account`
1. Visit the GCP console and create the json key for the new service account
1. Execute the command `scripts/set_secret.py --secret-name $DDS_GCP_CREDENTIALS_SECRET < gcp-credentials.json`

Now deploy using make:

    `make deploy`

## Relationship to DSS (AWS SSM Parameter Store)

Several configuration values need to be imported from the [data-store](https://github.com/HumanCellAtlas/data-store)
in order for Kharon to function correctly. These values are imported during deployment from the AWS SSM Parameter
Store `/dcp/dss/${DDS_DEPLOYMENT_STAGE}/environment`. When this parameter store is updated, Kharon should be
redeployed.

## Tests

1. Tests rely on the test fixtures bucket from the data-store repo, DSS_S3_BUCKET_TEST_FIXTURES. For instructions on
populating test fixtures, see https://github.com/HumanCellAtlas/data-store/blob/master/README.md
