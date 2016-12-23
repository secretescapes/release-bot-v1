import json
import os
import sys
import logging
import boto3

here = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(here, './vendored'))
import requests

from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

NOTIFY_SLACK_LAMBDA_NAME = os.environ.get("LAMBDA_NAME")


logger = logging.getLogger()
logger.setLevel(logging.INFO)
_lambda = boto3.client('lambda')

def notify_slack(event, context):
    logger.info("Notify slack invoked with event: %s" % event)
    text = event['text']

    url = os.environ['SLACK_WEBHOOK_URL']
    payload = {'text': text}
    headers = {'content-type': 'application/json'}

    logger.info("This payload will be sent do the webhook: %s" % payload)

    response = requests.post(url, data=json.dumps(payload), headers = headers)

    logger.info("Notification sent with statusCode: %s" % response.status_code)

    response = {
        "statusCode": response.status_code,
        "body": response.text
    }

    return response


def user_added_listener(event, context):
    logger.info("User Added Listener invoked with event: %s" % event)

    received_data = json.loads(event['Records'][0]['Sns']['Message'])

    payload = {'text': "*%s* has been added" % received_data['username']}
    response = _lambda.invoke(
        FunctionName=NOTIFY_SLACK_LAMBDA_NAME,
        InvocationType='Event',
        Payload=json.dumps(payload))
    return