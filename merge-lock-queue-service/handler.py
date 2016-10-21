import boto3
import botocore
import time

def add(event, context):
    username = _get_username(event)
    table = _getTable()

    if username is not None:
        try:
            _insert(username, table)
            message = "Hey %s! We have added you to the queue!" % username
        except botocore.exceptions.ClientError as e:
            message = _process_exception_for_insert(e, username)
    else:
        message = "You must provide a name"
    return {
            "message": message
        }

    

def list(event, context):
    table = _getTable()
    response = table.scan()
    items = sorted(response['Items'], key=lambda k: k['timestamp']) 

    return {
     "message": items
    }

def remove(event, context):
    username = _get_username(event)
    table = _getTable()

    if username is not None:
        try:
            _remove(username, table)
            message = "Hey %s! We have removed you from the queue!" % username
        except botocore.exceptions.ClientError as e:
            message = _process_exception_for_remove(e, username)
    else:
        message = "You must provide a name"
    return {
            "message": message
        }

def _get_username(event):
    params = event.get('body')
    return params.get('text')

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
                ConditionExpression = 'attribute_not_exists(username)'
            )

def _remove(username, table):
    response = table.delete_item(
        Key={
            'username': username
        }
    )

def _process_exception_for_remove(e):
    return "Something went wrong, please try later"
    
def _process_exception_for_insert(e, username):
    if e.response['Error']['Code'] != 'ConditionalCheckFailedException':
        return "Something went wrong, please try later"
    else:
        return "Sorry %s it seems you are already in the queue" % username

    
