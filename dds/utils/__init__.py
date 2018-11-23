import os
import boto3
import tempfile
from functools import lru_cache

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
