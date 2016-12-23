import json
import os
import sys
import logging

here = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(here, './vendored'))
import requests


logger = logging.getLogger()
logger.setLevel(logging.INFO)

def notify_slack(event, context):
    logger.info("Add invoke with event: %s" % event)
    text = event

    url = os.environ['SLACK_WEBHOOK_URL']
    payload = {'text': text}
    headers = {'content-type': 'application/json'}


    response = requests.post(url, data=json.dumps(payload), headers = headers)

    logger.info("Notification sent with statusCode: %s" % response.status_code)

    response = {
        "statusCode": response.status_code,
        "body": response.text
    }

    return response
