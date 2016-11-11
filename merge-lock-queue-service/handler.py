import boto3
import botocore
import time
import logging
import json
import urlparse
from decimal import Decimal
import os
import sys


here = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(here, './vendored'))
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)



def default(obj):
    if isinstance(obj, Decimal):
        return str(obj)
    raise TypeError

def add(event, context):
    try:
        logger.info("Add invoke with event: %s" % event)
        try:
            username = _getParameters(event['body'])
        except Exception as e:
            logger.error(e)
            return _responseError(400, "You must provide a username")

        if username is not None:
            #TODO: HARDCODED URL
            response = requests.get("https://r9mnwy3vfi.execute-api.eu-west-1.amazonaws.com/dev/user-service/user/%s" % username)
            if response.status_code == 400:
                return _responseError(402, "The user is not registered")
            elif response.status_code != 200:
                return _responseError(500, "Unexpected error")
            try:
                _insert_to_queue(username)
                return {
                    "statusCode": 200
                }

            except botocore.exceptions.ClientError as e:
                return _process_exception_for_insert(e, username)
        else:
            return _responseError(400, "You must provide a username")

    except Exception as e:
        logger.error(e)
        return {
            "statusCode": 500,
            "body": '{"error": "Unexpected error"}'
        }

def list(event, context):
    try:
        return {
            "statusCode": 200,
            "body": '{"queue": %s}' % json.dumps(_get_queue(), default=default)
        }
    except Exception as e:
        logger.error('Exception: %s' % e)
        return {
            "statusCode": 500,
            "body": '{"error":"Unexpected Error"}'
        }

def remove(event, context):
    logger.info("Remove invoke with event: %s" % event)
    try:
        username = _getParameters(event['body'])
    except Exception as e:
        logger.error(e)
        return {
            "statusCode": 400,
            "body": '{"error":"You must provide a username"}'
        }
    if username is not None:
        try:
            username = _getParameters(event['body'])
            table = _getTable('merge-lock')
            _remove(username, table)
            return {
                "statusCode": 200
            }

        except Exception as e:
            return _process_exception_for_remove(e, username)
    else:
        return {
            "statusCode": 400,
            "body": '{"error":"You must provide a username"}'
        }

def pop(event, context):
    try:
        username = event['pathParameters']['username']
        top_user = _get_top_user()
        if not username or username != top_user:
            return _responseError(400, "The user provided must be at the top of the queue")
        
        if (top_user):
            table = _getTable('merge-lock')
            _remove(top_user, table)
            return {
                "statusCode": 200,
                "body": '{"user": "%s"}' % top_user
            }
        else:
            return {
                "statusCode": 200
            }
    except Exception as e:
        logger.error(e)
        return _responseError(500, "Unexpected Error")

def _responseError(status_code, error_msg):
    return {
            "statusCode": status_code,
            "body": '{"error": "%s"}' % error_msg
        }

def _get_top_user():
    queue = _get_queue()
    if (len(queue) > 0):
        return queue[0]['username']    
    else:
        None

def _get_queue():
    table = _getTable('merge-lock')
    response = table.scan()
    logger.info("Response: %s" % response)
    return sorted(response['Items'], key=lambda k: k['timestamp'])

def _get_username(event):
    try:
        params = event['body']
        return params['username']
    except KeyError as e:
        logger.error("Unknown key %s" %s)
    

def _getTable(table_name):
    dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
    return dynamodb.Table(table_name)

def _insert_to_queue(username):
    table = _getTable('merge-lock')
    timestamp = int(round(time.time() * 1000))
    return table.put_item (
                Item = {
                    'username': username,
                    'timestamp': timestamp
                },
                ConditionExpression = 'attribute_not_exists(username)'
            )

def _insert(item, table):
    return table.put_item (
                Item = item
            )

def _remove(username, table):
    table.delete_item(
        Key = {
            'username': username
        },
        ConditionExpression = 'attribute_exists(username)'
    )

def _getParameters(body):
    parsed = urlparse.parse_qs(body)
    return parsed['username'][0]

def _process_exception_for_remove(e, username):
    if e.response['Error']['Code'] != 'ConditionalCheckFailedException':
        return {
            "statusCode": 500,
            "body": '{"error": "Unexpected Error"}'
        }
    else:
        return {
            "statusCode": 401,
            "body": '{"error": "User %s was not in the queue"}' % username
        }

def _process_exception_for_insert(e, username):
    if e.response['Error']['Code'] != 'ConditionalCheckFailedException':
        return {
            "statusCode": 500,
            "body": '{"error": "Unexpected Error"}'
        }
    else:
        return {
            "statusCode": 401,
            "body": '{"error": "User %s already in the queue"}' % username
        }

    
