# HCA Kharon: The Human Cell Atlas Data Deletion System

This repository contains AWS infrastructure definitions and procedures to carry out data deletions in the Data Storage System.

## Installing dependencies

1. Install `terraform` by following the instructions in [Install Terraform](https://www.terraform.io/intro/getting-started/install.html)

## Environment Variables

Environment variables are required for test and deployment. The required environment variables and their default values
are in the file `environment`. To customize the values of these environment variables:

1. Copy `environment.local.example` to `environment.local`
1. Edit `environment.local` to add custom entries that override the default values in `environment`
    
Run `source environment` now and whenever these environment files are modified.

## Deployment

1. Deploy the GCP service account with `make gcp-service-account`
1. Visit the GCP console and create the json key for the new service account
1. Execute the command `scripts/set_secret.py --secret-name $GOOGLE_APPLICATION_CREDENTIALS_SECRETS_NAME < gcp-credentials.json`

Now deploy using make:

    `make deploy`
