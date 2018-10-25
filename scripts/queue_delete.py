#!/usr/bin/env python
"""
Add a key, or a file containing a list of keys, to the deletion queue.
keys should have the format:
    {type}/{uuid}.{version}
e.g.
    bundles/0ec72eee-2087-4203-bccf-c92e4d79f110.2018-10-10T233759.699353Z
"""
import os
import json
import boto3
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed


stage = os.environ['DDS_DEPLOYMENT_STAGE']
account_id = boto3.client("sts").get_caller_identity()['Account']
region = os.environ['AWS_DEFAULT_REGION']
_queue_url = f"https://sqs.{region}.amazonaws.com/{account_id}/dds-delete-{stage}"
sqs_client = boto3.client("sqs")


def enqueue(key):
    sqs_client.send_message(
        QueueUrl=_queue_url,
        MessageBody=json.dumps({"key":key}),
    )


def _enqueue_batch(keys):
    assert 10 >= len(keys)
    ids = [key.split("/", 1)[1].split(".", 1)[0]  for key in keys]
    sqs_client.send_message_batch(
        QueueUrl=_queue_url,
        Entries=[
            dict(Id=id, MessageBody=json.dumps({"key":key}))
            for id, key in zip(ids, keys)
        ]
    )

def enqueue_batch(keys, parallel=True):
    chunks = list()
    while keys:
        chunks.append(keys[:10])
        keys = keys[10:]

    if parallel:
        with ThreadPoolExecutor(10) as executor:
            executor.map(_enqueue_batch, chunks)
    else:
        for chunk in chunks:
            _enqueue_batch(chunk)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("key_or_file")
    parser.add_argument("-d", "--stage", default="dev", choices=["dev", "integration", "staging", "prod"])
    args = parser.parse_args()

    if os.path.isfile(args.key_or_file):
        with open(args.key_or_file, "r") as fh:
            keys = fh.read().split()
        enqueue_batch(keys)
    else:
        enqueue(args.key_or_file)
