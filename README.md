# Kharon: The Data Store Deletion System

This repository contains AWS infrastructure definitions and procedures to carry out data deletions in the
[Data Storage System (DSS)](https://github.com/DataBiosphere/data-store).

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

    make deploy

## Relationship to DSS (AWS SSM Parameter Store)

Several configuration values need to be imported from the [data-store](https://github.com/DataBiosphere/data-store)
in order for Kharon to function correctly. These values are imported during deployment from the AWS SSM Parameter
Store `${DDS_SECRETS_STORE}/${DDS_DEPLOYMENT_STAGE}/environment`. When this parameter store is updated, Kharon should be
redeployed.

## Tests

1. Tests rely on the test fixtures bucket from the data-store repo, `DSS_S3_BUCKET_TEST_FIXTURES`. For instructions on
populating test fixtures, see https://github.com/DataBiosphere/data-store/blob/master/README.md

## Inclusion List Population

Writing very large inclusion lists to the dynamodb table can error unexpectedly, its best to break down large
whitelists into smaller segments, then upload each segment. The follow make commands can help:

```
# ${staging_dir} can be a new directory, it will be created as needed
make create-inclusion-list-parts INCLUSIONLIST=${inclusion_list} DIR=${staging_dir}
while true; do make populate-inclusion-list-parts DIR=${staging_dir} && break; done
```

These commands will split the large whitelist into smaller segments, then attempt to upload each whitelist to the 
dynamodb table. As the make command runs it will move completed segments into `${staging_dir}/complete/`, if the make
command errors, it will rerun until it completes successfully. 
