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
            "text": message
        }

    

def list(event, context):
    table = _getTable()
    response = table.scan()
    message = _get_queue()

    return {
     "text": message
    }

def remove(event, context):
    username = _get_username(event)
    table = _getTable()
    message = _remove_with_message(username, table)
    
    return {
            "text": message
        }

def pop(event, context):
    top_user = _get_top_user()
    if (top_user):
        table = _getTable()
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
    table = _getTable()
    response = table.scan()
    return sorted(response['Items'], key=lambda k: k['timestamp'])

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
    table.delete_item(
        Key = {
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

    
