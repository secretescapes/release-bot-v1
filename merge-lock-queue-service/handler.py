import boto3
import botocore
import time
import logging
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)

_lambda = boto3.client('lambda')
_sns = boto3.client('sns')

def add(event, context):
    try:
        logger.info("Add dispatcher invoke with event: %s" % event)
        username = _get_username(event)

        if username is not None:
            try:
                _insert_to_queue(username)
                message = "Hey %s! We have added you to the queue!" % username
            except botocore.exceptions.ClientError as e:
                message = _process_exception_for_insert(e, username)
        else:
            message = "You must provide a name"
        return {
                "text": message
            }
    except Exception as e:
        logger.error(e)

def add_dispatcher(event, context):    
    logger.info("Add dispatcher invoke with event: %s" % event)
    for record in event['Records']:
        try:
            eventItem = json.loads(record['Sns']['Message'])
            response_url = eventItem['response_url']
            requester = eventItem['requester']
            username = eventItem['username']
            response = _lambda.invoke(
                #TODO find a way to get the function
                FunctionName='merge-lock-queue-service-dev-add',
                Payload='{"body": {"username": "%s"}}' % (username)
            )
            response_text = json.loads(response['Payload'].read())
            logger.info("Add response payload: %s" % response_text)
            _sns.publish(
                TopicArn='arn:aws:sns:eu-west-1:015754386147:addResponse',
                Message='{"response_url": "%s","requester":"%s","payload": "%s"}' % (response_url, requester, response_text['text']) ,
                MessageStructure='string'
            )
            

        except KeyError as e:
            logger.error("Unrecognized key: %s" % e)

def list(event, context):
    table = _getTable('merge-lock')
    response = table.scan()
    message = _get_queue()
    return {
        "text": message
    }

def list_dispatcher(event, context):
    logger.info("List dispatcher invoke with event: %s" % event)
    for record in event['Records']:
        try:
            eventItem = json.loads(record['Sns']['Message'])
            logger.info("Processing event: %s" % eventItem)
            response_url = eventItem['response_url']
            requester = eventItem['requester']
            response = _lambda.invoke(
                #TODO find a way to get the function
                FunctionName='merge-lock-queue-service-dev-list'
            )
            _sns.publish(
                TopicArn='arn:aws:sns:eu-west-1:015754386147:listQueueResponse',
                Message='{"response_url": "%s","requester":"%s","payload": "%s"}' % (response_url, requester, _process_payload(response['Payload'].read())) ,
                MessageStructure='string'
            )
            

        except KeyError as e:
            logger.error("Unrecognized key: %s" % e)

def remove(event, context):
    username = _get_username(event)
    table = _getTable('merge-lock')
    message = _remove_with_message(username, table)
    
    return {
            "text": message
        }

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
    return sorted(response['Items'], key=lambda k: k['timestamp'])

def _get_username(event):
    try:
        params = event.get('body')
        return params.get('username')
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

def _process_payload(string):
    output = ""
    position = 0
    obj = json.loads(string)
    logger.info("obj: %s" % obj)
    logger.info("obj['text']: %s" % obj['text'])
    for item in obj['text']:
        position += 1
        output += "%d. %s " % (position, item['username'])
    return "%s" % output

def _process_exception_for_remove(e):
    return "Something went wrong, please try later"

def _process_exception_for_insert(e, username):
    if e.response['Error']['Code'] != 'ConditionalCheckFailedException':
        return "Something went wrong, please try later"
    else:
        return "Sorry %s it seems you are already in the queue" % username

    
