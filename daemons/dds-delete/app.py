"""
Queue driven deletion service
"""
import os
import sys
import json
import domovoi

pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), 'domovoilib'))  # noqa
sys.path.insert(0, pkg_root)  # noqa

import dds

app = domovoi.Domovoi()


@app.sqs_queue_subscriber("dds-delete-" + os.environ["DDS_DEPLOYMENT_STAGE"])
def launch_from_queue(event, context):
    for event_record in event["Records"]:
        message = json.loads(event_record["body"])
        dds.delete(message['key'])
