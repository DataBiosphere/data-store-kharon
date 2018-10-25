#!/usr/bin/env python
"""
Add every key in a replica to the deletion queue
"""
import os
import sys
import json
import boto3
import argparse
from functools import partial
from concurrent.futures import ThreadPoolExecutor, as_completed

pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))  # noqa
sys.path.insert(0, pkg_root)  # noqa

import dds
import queue_delete


def process_prefix(handle, bucket, pfx):
    keys = list()
    for key in handle.list(bucket, pfx):
        keys.append(key)
        if 1000 == len(keys):
            queue_delete.enqueue_batch(keys, parallel=False)
            keys = list()
    if len(keys):
        queue_delete.enqueue_batch(keys, parallel=False)


def enqueue_bucket(handle, bucket):
    digits = "0123456789abcdef"
    prefixes = [f"{kind}/{c}"
                for kind in ["blobs", "files", "bundles", "collections"]
                for c in digits]
    with ThreadPoolExecutor(10) as executor:
        futures = [executor.submit(process_prefix, handle, bucket, pfx)
                   for pfx in prefixes]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(e)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replica", default="aws", choices=["aws", "gcp"])
    parser.add_argument("-d", "--stage", default="dev", choices=["dev", "integration", "staging", "prod"])
    args = parser.parse_args()

    handle = dds.get_handle(args.replica)
    bucket = dds.BUCKETS[args.replica]

    enqueue_bucket(handle, bucket)
