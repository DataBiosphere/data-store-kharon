#!/usr/bin/env python
"""
Add every key in a replica to the deletion queue
"""
import os
import sys
import json
import argparse
from concurrent.futures import ThreadPoolExecutor

from dcplib.aws.sqs import SQSMessenger

pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))  # noqa
sys.path.insert(0, pkg_root)  # noqa

import utils
utils.prepare_environment()  # noqa
import dds


def process_prefix(handle, bucket, pfx):
    with SQSMessenger(utils.get_queue_url()) as sqsm:
        for key in handle.list(bucket, pfx):
            sqsm.send(json.dumps(dict(key=key)))

def enqueue_bucket(handle, bucket):
    digits = "0123456789abcdef"
    prefixes = [f"{kind}/{c}"
                for kind in ["collections", "bundles", "files", "blobs"]
                for c in digits]
    with ThreadPoolExecutor(10) as executor:
        executor.map(lambda pfx: process_prefix(handle, bucket, pfx), prefixes)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("replica", choices=["aws", "gcp"])
    args = parser.parse_args()

    handle = dds.get_handle(args.replica)
    bucket = dds.BUCKETS[args.replica]

    enqueue_bucket(handle, bucket)
