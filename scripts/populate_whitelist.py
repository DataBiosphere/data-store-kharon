#!/usr/bin/env python
"""
Add items to the deletion whitelist (items which will not be deleted)
Items must have the format:
{type}/{uuid}.{version}
e.g.
bundles/0d169eef-d82d-4717-9052-fcbef89e33bb.2018-10-04T161005.538315Z
or
files/004638ea-96a7-4daa-a68d-4943b599cf3b.2018-09-21T154601.404734Z
"""
import os
import sys
import json
import boto3
import argparse
from cloud_blobstore import BlobNotFoundError
from concurrent.futures import ThreadPoolExecutor, as_completed

pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))  # noqa
sys.path.insert(0, pkg_root)  # noqa

import utils
utils.prepare_environment()  # noqa
import dds


ddb_client = boto3.client("dynamodb")


def key_exists(handle, bucket, key):
    try:
        sz = handle.get_size(bucket, key)
        return True
    except BlobNotFoundError:
        return False


def find_references(handle, bucket, key):
    references = set()
    if key.startswith("collections") and key_exists(handle, bucket, key):
        manifest = json.loads(handle.get(bucket, key))
        for item in manifest['contents']:
            if "bundle" == item['type']:
                item_key = f"bundles/{item['uuid']}/{item['version']}"
            elif "file" == item['type']:
                item_key = f"files/{item['uuid']}/{item['version']}"
            else:
                continue
            references.add(item_key)
            references.update(
                find_references(handle, bucket, item_key)
            )
    elif key.startswith("bundles") and key_exists(handle, bucket, key):
        manifest = json.loads(handle.get(bucket, key))
        for file in manifest['files']:
            file_key = f"files/{file['uuid']}.{file['version']}"
            blob_key = f"blobs/{file['sha256']}.{file['sha1']}.{file['s3-etag']}.{file['crc32c']}"
            references.add(file_key)
            references.add(blob_key)
    elif key.startswith("files") and key_exists(handle, bucket, key):
        file = json.loads(handle.get(bucket, key))
        blob_key = f"blobs/{file['sha256']}.{file['sha1']}.{file['s3-etag']}.{file['crc32c']}"
        references.add(blob_key)
    return references


def populate_whitelist(keys, action):
    chunks = list()
    while(len(keys)):
        chunks.append(keys[:25])
        keys = keys[25:]

    attribute_lookup = "Key" if action == "DeleteRequest" else "Item"
    for chunk in chunks:
        request_items = {
            f"dds-whitelist-{os.environ['DDS_DEPLOYMENT_STAGE']}": [
                {
                    action : {
                        attribute_lookup : {
                            'key': {
                                'S': key
                            }
                        }
                    }
                }
            for key in chunk]
        }
        resp = ddb_client.batch_write_item(RequestItems=request_items)
        if resp['UnprocessedItems']:
            raise Exception("Unable to populate table")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("keys_file", help="File containing list of items with format {type}/{uuid}.{version}. One item per line.")
    parser.add_argument("--delete", help="removes items from the whitelist rather than inserting them", action="store_true")
    args = parser.parse_args()

    with open(args.keys_file, "r") as fh:
        whitelist = set(fh.read().split())

    handle = dds.get_handle("aws")
    bucket = dds.BUCKETS["aws"]

    with ThreadPoolExecutor(10) as executor:
        futures = [executor.submit(find_references, handle, bucket, key) for key in whitelist]
        results = [f.result() for f in as_completed(futures)]
        whitelist = whitelist.union(*results)

    action = "DeleteRequest" if args.delete else "PutRequest"
    populate_whitelist(list(whitelist), action=action)
