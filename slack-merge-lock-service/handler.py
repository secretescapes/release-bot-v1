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

_sns = boto3.client('sns')

def merge_lock(event, context):
    try:
        params = event.get('body')
        response_url = params.get('response_url')
        text = params.get('text').split()
        logger.info("Command received: %s" % text)

        if len(text) == 1 and text[0].lower() == 'list':
            return {"text":_list_request_handler(response_url)}
            # return {"text": "I am grabbing the info for you, just hang on a little bit..."}
        elif len(text) == 2 and text[0].lower() == 'add':
            username = text[1]
            _add_request_handler(response_url, username)
            return {"text": "I will try to add %s to the queue..." % (username)}
        elif len(text) == 2 and text[0].lower() == 'remove':
            username = text[1]
            _remove_request_handler(response_url, username)
            return {"text": "I will try to remove %s to the queue..." % (username)}
        else:
            return {"text": "unrecognized command, please try one of these:\n/lock list\n/lock add [username]\n/lock remove [username]"}
    except Exception as e:
        logger.error(e)
        return {"text": "Something went really wrong, sorry"}

def dispatcher_responses(event, context):
    logger.info("List dispatcher invoke with event: %s" % event)
    for record in event['Records']:
        try:
            eventItem = json.loads(record['Sns']['Message'])
            response_url = eventItem['response_url']
            requester = eventItem['requester']
            if requester == "SLACK_MERGE_LOCK_SERVICE":
                response_text = "{'text': '%s'}" % eventItem['payload']
                logger.info("Response body: %s" % response_text)
                requests.post(response_url, data = response_text)
        except KeyError as e:
            logger.error("Unrecognized key: %s" % e)


def _remove_request_handler(response_url, username):
    _sns.publish(
        TopicArn='arn:aws:sns:eu-west-1:015754386147:removeRequest',
        Message='{"response_url": "%s", "requester":"SLACK_MERGE_LOCK_SERVICE", "username": "%s"}' % (response_url, username),
        MessageStructure='string'
    )

def _add_request_handler(response_url, username):
    _sns.publish(
        TopicArn='arn:aws:sns:eu-west-1:015754386147:addRequest',
        Message='{"response_url": "%s", "requester":"SLACK_MERGE_LOCK_SERVICE", "username": "%s"}' % (response_url, username),
        MessageStructure='string'
    )

def _list_request_handler(response_url):
    #TODO: HARDCODED URL!!
    response = requests.get("https://5ywhqv93l9.execute-api.eu-west-1.amazonaws.com/dev/mergelock/list")
    if response.status_code == 200:
        return _format_list_response(response.json())
    else:
        return {'text': 'Something went wrong, please try again'}

def _format_list_response(json):
    i = 1
    text = 'Here is the current status of the queue:\n'
    for item in json:
        if i == 1:
            text += "*%d. %s*\n" % (i, item['username'])
        else:
            text += "%d. %s\n" % (i, item['username'])
        i+= 1
    return text

def _getTable(table_name):
    dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
    return dynamodb.Table(table_name)

def _insert(item, table):
    return table.put_item (
                Item = item
            )
