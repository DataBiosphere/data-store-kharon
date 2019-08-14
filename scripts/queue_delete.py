#!/usr/bin/env python
"""
Add a key, or a file containing a list of keys, to the deletion queue.
keys should have the format:
    {type}/{uuid}.{version}
e.g.
    bundles/0ec72eee-2087-4203-bccf-c92e4d79f110.2018-10-10T233759.699353Z
"""
import os
import sys
import json
import argparse

from dcplib.aws.sqs import SQSMessenger

pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))  # noqa
sys.path.insert(0, pkg_root)  # noqa

import utils


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("key_or_file")
    args = parser.parse_args()

    with SQSMessenger(utils.get_queue_url()) as sqsm:
        if os.path.isfile(args.key_or_file):
            with open(args.key_or_file, "r") as fh:
                for line in fh:
                    sqsm.send(json.dumps(dict(key=line.strip())))
        else:
            sqsm.send(json.dumps(dict(key=args.key_or_file)))
