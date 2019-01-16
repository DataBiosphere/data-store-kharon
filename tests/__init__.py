import os
import sys
import time
import json
import boto3
import logging
import functools

pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))  # noqa
sys.path.insert(0, pkg_root)  # noqa

dss_parms = json.loads(
    boto3.client("ssm").get_parameter(
        Name=f"/dcp/dss/{os.environ['DDS_DEPLOYMENT_STAGE']}/environment"
    )['Parameter']['Value']
)

os.environ['DSS_S3_BUCKET'] = dss_parms['DSS_S3_BUCKET']
os.environ['DSS_GS_BUCKET'] = dss_parms['DSS_GS_BUCKET']
os.environ['DSS_ES_ENDPOINT'] = dss_parms['DSS_ES_ENDPOINT']

import dds.util  # noqa

logger = logging.getLogger(__name__)
if not os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = dds.util.get_gcp_credentials_file().name

def eventually(timeout: float, interval: float, errors: set = {AssertionError}):
    """
    @eventually runs a test until all assertions are satisfied or a timeout is reached.
    :param timeout: time until the test fails
    :param interval: time between attempts of the test
    :param errors: the exceptions to catch and retry on
    :return: the result of the function or a raised assertion error
    """
    def decorate(func):
        @functools.wraps(func)
        def call(*args, **kwargs):
            timeout_time = time.time() + timeout
            error_tuple = tuple(errors)
            while True:
                try:
                    return func(*args, **kwargs)
                except error_tuple as e:
                    if time.time() >= timeout_time:
                        raise
                    logger.debug("Error in %s: %s. Retrying after %s s...", func, e, interval)
                    time.sleep(interval)

        return call

    return decorate
