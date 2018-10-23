#!/usr/bin/env python
# coding: utf-8
"""
Tests for dds
"""
import os
import sys
import json
import boto3
import random
import unittest

pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))  # noqa
sys.path.insert(0, pkg_root)  # noqa

stage = os.environ['DDS_DEPLOYMENT_STAGE']
parm = boto3.client("ssm").get_parameter(Name=f"/dcp/dss/{stage}/environment")
os.environ.update(json.loads(parm['Parameter']['Value']))


import dds  # noqa


class TestConfig(unittest.TestCase):
    def test_something(self):
        # TODO (xbrianh): instead of deleting a random bundle,
        # upload one and delete it
        aws_handle = dds.get_handle("aws")
        aws_bucket = dds.BUCKETS["aws"]
        gcp_handle = dds.get_handle("gcp")
        gcp_bucket = dds.BUCKETS["gcp"]

        pfx = f"bundles/{random.choice('0123456789abcdef')}"
        for bundle_key in aws_handle.list(dds.BUCKETS["aws"], pfx):
            break
        bundle_manifest = json.loads(aws_handle.get(aws_bucket, bundle_key))
        keys = [
            (
                f"files/{file['uuid']}.{file['version']}",
                f"blobs/{file['sha256']}.{file['sha1']}.{file['s3-etag']}.{file['crc32c']}",
            )
            for file in bundle_manifest['files']
        ]
        dryrun = False
        for file_key, blob_key in keys:
            dds.delete(blob_key, dryrun=dryrun)
            dds.delete(file_key, dryrun=dryrun)
            with self.assertRaises(dds.BlobNotFoundError):
                aws_handle.get(aws_bucket, blob_key)
            with self.assertRaises(dds.BlobNotFoundError):
                gcp_handle.get(gcp_bucket, blob_key)
        dds.delete(bundle_key, dryrun=dryrun)
        bundle_fqid = bundle_key.split("/")[1]
        dds.get_es_client().indices.refresh("_all")
        res = dds.get_es_client().search(
            index="_all",
            body= {"query":{"terms":{"_id":[bundle_fqid]}}}
        )
        self.assertEqual(0, res['hits']['total'])

if __name__ == '__main__':
    unittest.main()
