#!/usr/bin/env python
"""
Verify that every item on the inclusion list exists in every replica.
"""
import os
import sys
from cloud_blobstore import BlobNotFoundError
from concurrent.futures import ThreadPoolExecutor, as_completed

pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))  # noqa
sys.path.insert(0, pkg_root)  # noqa

import utils
utils.prepare_environment()  # noqa
import dds

missing = dict()
failed = False

for replica in dds.BUCKETS:
    handle = dds.get_handle(replica)
    bucket = dds.BUCKETS[replica]

    missing[replica] = list()
    for item in dds.get_whitelist():
        try:
            handle.get_size(bucket, item)
        except BlobNotFoundError:
            print(f"missing {item} from {replica}")
            failed = True

sys.exit(1 if failed else 0)
