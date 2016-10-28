import boto3
import botocore
import time
import logging
import json

import os
import sys

here = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(here, "./vendored"))
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def dispatcher(event, context):
    logger.info("Event received by dispatcher: %s" % event)
    # for record in event['Records']:
    #     try:
    #         eventItem = record['dynamodb']['NewImage']
    #         if (eventItem['eventType']['S'].upper() == "LIST_RESPONSE"):
    #             response_url = eventItem['response_url']['S']
    #             payload = eventItem['payload']['S']
    #             logger.info("response url: %s" % response_url)
    #             logger.info("payload: %s" % payload)
    #             response_text = "{'text': %s}" % _process_payload(payload)
    #             logger.info("Response body: %s" % response_text)
    #             requests.post(response_url, data = response_text)
    #         else:
    #             pass
    #     except KeyError as e:
    #         logger.error("Unrecognized key %s" % e)
    
def merge_lock(event, context):
    params = event.get('body')
    response_url = params.get('response_url')
    text = params.get('text').split()
    if len(text) == 1 and text[0].lower() == 'list':
        timestamp = int(round(time.time() * 1000))
        item = {
            'timestamp': timestamp,
            'eventType': 'LIST_REQUEST',
            'response_url': response_url
        }
        table = _getTable('events')
        _insert(item, table)
    else:
        return {
            "text": "unrecognized command"
        }


def _process_payload(payload):
    obj = json.loads(payload)
    output = ""
    position = 0
    for item in obj['text']:
        position += 1
        output += str(position)+ '. ' +item['username'] + '\n'
    return "'%s'" % output

def _getTable(table_name):
    dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
    return dynamodb.Table(table_name)

def _insert(item, table):
    return table.put_item (
                Item = item
            )
