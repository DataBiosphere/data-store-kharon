import os
import json
import boto3
import tempfile
from functools import lru_cache

from dcplib.aws.clients import sqs

@lru_cache()
def get_gcp_credentials_file():
    """
    Aquire GCP credentials from AWS secretsmanager and write them to a temporary file.
    A reference to the temporary file is saved in lru_cache so it is not cleaned up
    before a GCP client is instantiated.

    Normal usage is local execution. For cloud execution (AWS Lambda, etc.),
    credentials are typically available at GOOGLE_APPLICATION_CREDENTIALS.
    """
    secret_store = os.environ['DDS_SECRETS_STORE']
    stage = os.environ['DDS_DEPLOYMENT_STAGE']
    secret_id = f"{secret_store}/{stage}/gcp-credentials.json"
    resp = boto3.client("secretsmanager").get_secret_value(SecretId=secret_id)
    tf = tempfile.NamedTemporaryFile("w")
    tf.write(resp['SecretString'])
    tf.flush()
    return tf

def prepare_environment():
    """
    Populate env vars stored in AWS SSM parameter store and AWS Secrets Manager.
    """
    dss_parms = json.loads(
        boto3.client("ssm").get_parameter(
            Name=f"/{os.environ['DDS_SECRETS_STORE']}/{os.environ['DDS_DEPLOYMENT_STAGE']}/environment"
        )['Parameter']['Value']
    )
    os.environ['DSS_S3_BUCKET'] = dss_parms['DSS_S3_BUCKET']
    os.environ['DSS_GS_BUCKET'] = dss_parms['DSS_GS_BUCKET']
    os.environ['DSS_ES_ENDPOINT'] = dss_parms['DSS_ES_ENDPOINT']
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = get_gcp_credentials_file().name

def get_queue_url():
    return sqs.get_queue_url(QueueName=f"dds-delete-{os.environ['DDS_DEPLOYMENT_STAGE']}")['QueueUrl']
