import os
import boto3
import logging
import functools
from google.cloud.storage import Client
from cloud_blobstore import BlobNotFoundError
from cloud_blobstore.s3 import S3BlobStore
from cloud_blobstore.gs import GSBlobStore
from elasticsearch import Elasticsearch, RequestsHttpConnection
from elasticsearch import TransportError
from requests_aws4auth import AWS4Auth

logger = logging.getLogger()
logger.setLevel(logging.INFO)

BUCKETS = dict(
    aws=os.environ['DSS_S3_BUCKET'],
    gcp=os.environ['DSS_GS_BUCKET'],
)

@functools.lru_cache()
def get_es_client():
    host = os.environ['DSS_ES_ENDPOINT']
    port = 443
    session = boto3.session.Session()
    current_credentials = session.get_credentials().get_frozen_credentials()
    es_auth = AWS4Auth(
        current_credentials.access_key, current_credentials.secret_key,
        session.region_name, "es", session_token=current_credentials.token
    )
    es_client = Elasticsearch(
        hosts=[dict(host=host, port=port)],
        timeout=10,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
        http_auth=es_auth
    )
    return es_client

@functools.lru_cache()
def get_handle(replica):
    if "aws" == replica:
        return S3BlobStore(boto3.client("s3"))
    elif "gcp" == replica:
        return GSBlobStore(Client())
    else:
        msg = f"Unknown replica {replica}"
        logger.error(msg)
        raise Exception(msg)

@functools.lru_cache()
def get_whitelist():
    ddb_client = boto3.client('dynamodb')
    items = ddb_client.scan(TableName=f"dds-whitelist-{os.environ['DDS_DEPLOYMENT_STAGE']}")['Items']
    keys = {item['key']['S'] for item in items}
    return keys

def deindex(key):
    if key.startswith("bundles/"):
        es_client = get_es_client()
        fqid = key.split("/")[1]
        es_client.delete_by_query(
            index="_all",
            body= {"query":{"terms":{"_id":[fqid]}}}
        )
        logger.info(f"Removed {fqid} from all ES indices")

def _delete(replica, key):
    try:
        handle = get_handle(replica)
        bucket = BUCKETS[replica]
        handle.get_size(bucket, key)
        handle.delete(bucket, key)
        logger.info(f"Deleted {replica} {bucket}/{key}")
    except BlobNotFoundError:
        pass

def delete(key):
    if key in get_whitelist():
        logger.debug(f"Not deleting whitelisted {key}")
    else:
        for replica in BUCKETS:
            _delete(replica, key)
        deindex(key)
