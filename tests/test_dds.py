#!/usr/bin/env python
# coding: utf-8

import os
import io
import sys
import hca
import json
import uuid
import pytz
import boto3
import random
import unittest
import datetime
from cloud_blobstore import BlobNotFoundError

pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))  # noqa
sys.path.insert(0, pkg_root)  # noqa

from tests import eventually

stage = os.environ['DDS_DEPLOYMENT_STAGE']
test_fixtures_bucket = os.environ['DSS_S3_BUCKET_TEST_FIXTURES']
parm = boto3.client("ssm").get_parameter(Name=f"/dcp/dss/{stage}/environment")
os.environ.update(json.loads(parm['Parameter']['Value']))


import dds  # noqa


class TestConfig(unittest.TestCase):
    def setUp(self):
        swag_url = f"https://dss.{stage}.data.humancellatlas.org/v1/swagger.json"
        self.ddb_client = boto3.client('dynamodb')
        self.dss_client = hca.dss.SwaggerClient(swagger_url=swag_url)
        self.handles = {
            "aws": dds.get_handle("aws"),
            "gcp": dds.get_handle("gcp"),
        }
        self.version = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M%S.%fZ")

    def test_delete_synced_bundle(self):
        bundle_manifest = self._put_and_sync_bundle()['bundle']
        bundle_key = f"bundles/{bundle_manifest['uuid']}.{bundle_manifest['version']}"
        bundle_fqid = bundle_key.split("/")[1]

        self.assertGreater(self._bundle_es_hits(bundle_fqid), 0)

        keys = [
            (
                f"files/{file['uuid']}.{file['version']}",
                f"blobs/{file['sha256']}.{file['sha1']}.{file['s3_etag']}.{file['crc32c']}",
            )
            for file in bundle_manifest['files']
        ]

        for file_key, blob_key in keys:
            dds.delete(blob_key)
            dds.delete(file_key)
            self._assertNotExists("aws", blob_key)
            self._assertNotExists("gcp", blob_key)

        dds.delete(bundle_key)
        self.assertEqual(self._bundle_es_hits(bundle_fqid), 0)

    def test_delete(self):
        for replica in dds.BUCKETS.keys():
            with self.subTest(replica):
                key = self._put_unsynced_unindex_object(replica)
                self._assertExists(replica, key)
                dds.delete(key)
                self._assertNotExists(replica, key)

    def test_delete_whitelist(self):
        for replica in dds.BUCKETS.keys():
            with self.subTest(replica):
                key = self._put_unsynced_unindex_object(replica)
                self._assertExists(replica, key)

                # Add key to whitelist
                self._put_whitelist_item(key)
                dds.get_whitelist.cache_clear()
                self.assertIn(key, dds.get_whitelist())

                # Should not be able to delete whitelsited key
                dds.delete(key)
                self._assertExists(replica, key)

                # Remove key from whitelist
                self._delete_whitelist_item(key)
                dds.get_whitelist.cache_clear()
                self.assertNotIn(key, dds.get_whitelist())

                # Should be able to delete key
                dds.delete(key)
                self._assertNotExists(replica, key)

    @eventually(30, 2, {BlobNotFoundError})
    def _assertExists(self, replica, key):
        handle = self.handles[replica]
        bucket = dds.BUCKETS[replica]
        handle.get_size(bucket, key)

    def _assertNotExists(self, replica, key):
        handle = self.handles[replica]
        bucket = dds.BUCKETS[replica]
        with self.assertRaises(dds.BlobNotFoundError):
            handle.get_size(bucket, key)

    @eventually(10, 2)
    def _bundle_es_hits(self, bundle_fqid):
        """
        Return number of search results for bundle_fqid in the ES index
        """
        dds.get_es_client().indices.refresh()
        res = dds.get_es_client().search(
            index="_all",
            body={"query": {"terms": {"_id": [bundle_fqid]}}}
        )
        return res['hits']['total']

    def _put_unsynced_unindex_object(self, replica):
        """
        Upload an un-syncable, un-indexable  object to DSS
        """
        key = f"files/{uuid.uuid4()}.{self.version}"
        handle = self.handles[replica]
        bucket = dds.BUCKETS[replica]
        with io.BytesIO(b"this is a test file") as fh:
            handle.upload_file_handle(bucket, key, fh)
        self._assertExists(replica, key)
        return key

    def _put_and_sync_bundle(self):
        """
        Upload a bundle to DSS and wait for it to sync
        """
        file_uuid_1 = str(uuid.uuid4())
        file_uuid_2 = str(uuid.uuid4())
        bundle_uuid = str(uuid.uuid4())

        self.dss_client.put_file(
            replica="aws",
            uuid=file_uuid_1,
            version=self.version,
            source_url=f"s3://{test_fixtures_bucket}/test_good_source_data/0",
            creator_uid=1,
        )

        self.dss_client.put_file(
            replica="aws",
            uuid=file_uuid_2,
            version=self.version,
            source_url=f"s3://{test_fixtures_bucket}/test_good_source_data/1",
            creator_uid=1,
        )

        self.dss_client.put_bundle(
            replica="aws",
            uuid=bundle_uuid,
            creator_uid=1,
            version=self.version,
            files=[
                {
                    "indexed": False,
                    "name": "file_1",
                    "uuid": file_uuid_1,
                    "version": self.version,
                },
                {
                    "indexed": False,
                    "name": "file_2",
                    "uuid": file_uuid_1,
                    "version": self.version,
                },
            ]
        )

        bundle_manifest = self.dss_client.get_bundle(
            replica="aws",
            uuid=bundle_uuid,
            version=self.version
        )

        self._assertExists("gcp", f"bundles/{bundle_uuid}.{self.version}")

        return bundle_manifest

    def _put_whitelist_item(self, key):
        self.ddb_client.put_item(
            TableName=f"dds-whitelist-{stage}",
            Item={
                'key': {
                    'S': key
                }
            }
        )

    def _delete_whitelist_item(self, key):
        self.ddb_client.delete_item(
            TableName=f"dds-whitelist-{stage}",
            Key={
                'key': {
                    'S': key
                }
            }
        )


if __name__ == '__main__':
    unittest.main()
