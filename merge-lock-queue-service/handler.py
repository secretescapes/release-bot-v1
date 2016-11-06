import boto3
import botocore
import time
import logging
import json
import urlparse

logger = logging.getLogger()
logger.setLevel(logging.INFO)

from decimal import Decimal

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
            return {
                "statusCode": 400,
                "body": '{"error":"You must provide a username"}'
            }

        if username is not None:
            try:
                _insert_to_queue(username)
                return {
                    "statusCode": 200
                }

            except botocore.exceptions.ClientError as e:
                return _process_exception_for_insert(e, username)
        else:
            return {
                "statusCode": 400,
                "body": '{"error":"You must provide a username"}'
            }

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
    username = _get_username(event)
    table = _getTable('merge-lock')
    return _remove_with_message(username, table)

def pop(event, context):
    top_user = _get_top_user()
    if (top_user):
        table = _getTable('merge-lock')
        _remove(top_user, table)
        message = "%s has been removed from the queue!" % top_user
    else:
        message = "Queue is empty!"

    return {
            "text": message
        }


        
def _remove_with_message(username, table):
    if username is not None:
        try:
            _remove(username, table)
            message = "Hey %s! We have removed you from the queue!" % username
        except botocore.exceptions.ClientError as e:
            message = _process_exception_for_remove(e, username)
    else:
        message = "You must provide a name"
    return message

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
        }
    )

def _getParameters(body):
    parsed = urlparse.parse_qs(body)
    return parsed['username'][0]

def _get_params_with_username(item):
    return (item['response_url'],
            item['requester'],
            item['username'])

def _process_exception_for_remove(e):
    return "Something went wrong, please try later"

def _process_exception_for_insert(e, username):
    if e.response['Error']['Code'] != 'ConditionalCheckFailedException':
        return {
            "statusCode": 500,
            "body": '{"error": "Unexpected Error"}'
        }
    else:
        return {
            "statusCode": 401,
            "body": '{"error": "User already in the queue"}'
        }

    
