import boto3
import botocore
import logging
import json
import os
import sys
from commons import publish_to_sns


here = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(here, './vendored'))
sys.path.append(os.path.join(here, './commons'))
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)

from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

stage = os.environ.get("STAGE")
region = os.environ.get("REGION")
def pipelineTriggerFunction(event, context):
    logger.info("Pipeline Trigger function invoked with event: %s" % event)

    return
