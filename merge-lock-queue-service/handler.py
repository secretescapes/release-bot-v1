import boto3
import botocore
import time

def add(event, context):
    username = _get_username(event)
    table = _getTable()

    try:
        _insert(username, table)
        message = "Hey %s! We have added you to the queue!" % username
    except botocore.exceptions.ClientError as e:
        message = _process_exception(e, username)
    
    return {
        "message": message
    }

def list(event, context):
    table = _getTable()
    response = table.scan()
    return {
     "message": response
    }

def _get_username(event):
    params = event.get('path')
    return params.get('username')

def _getTable():
    dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
    return dynamodb.Table('merge-lock')

def _insert(username, table):
    timestamp = int(round(time.time() * 1000))
    return table.put_item (
                Item = {
                    'username': username,
                    'timestamp': timestamp
                },
                ConditionExpression='attribute_not_exists(username)'
            )

def _process_exception(e, username):
    if e.response['Error']['Code'] != 'ConditionalCheckFailedException':
        raise
    else:
        return "Sorry %s it seems you are already in the queue" % username

    
