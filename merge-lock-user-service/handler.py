import json
import boto3
import logging
import urlparse
from boto3.dynamodb.conditions import Key, Attr

logger = logging.getLogger()
logger.setLevel(logging.INFO)

_client = boto3.client('dynamodb')
_dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')

def update(event, context):
    logger.info("Create invoked with event: %s" % event)
    try:
        logger.info("Create invoked with event: %s" % event)
        (username, githubUsername) = _getParameters(event['body'])
        item = {
            "username": username,
            "githubUsername": githubUsername
        }
        table = _getTable('users')
        response = _insert(item, table)
        logger.info("Response: %s" %response)
        if (response['ResponseMetadata']['HTTPStatusCode'] == 200):
            return {
                "statusCode": 200
            }
        else:
            return {
                "statusCode": 500,
                "body": '{"error":"Database Error"}'
            }

    except KeyError as key:
        logger.error("Missing key: %s" % key)
        return {
                "statusCode": 400,
                "body": '{"error":"Malformed Request"}'
            }
   

def list_all(event, context):
    logger.info("List All invoked with event: %s" % event)
    table = _getTable('users')
    response = table.scan()
    return {
            "statusCode": 200,
            "body": json.dumps(response['Items'])
        }

def list(event, context):
    logger.info("List invoked with event: %s" % event)
    username = _getUsernameFromPath(event)
    table = _getTable('users')
    response = table.query(
        KeyConditionExpression=Key('username').eq(username)
    )
    return {
            "statusCode": 200,
            "body": json.dumps(response['Items'])
        }

def reverseList(event, context):
    logger.info("Reverse List invoked with event: %s" % event)
    username = _getUsernameFromPath(event)
    table = _getTable('users')
    response = table.scan(
        FilterExpression = Attr('githubUsername').eq(username)
    )
    return {
        "statusCode": 200,
        "body": json.dumps(response['Items'])
    }
    
def delete(event, context):
    logger.info("Delete invoked with event: %s" % event)
    username = _getUsernameFromPath(event)
    table = _getTable('users')
    response = table.delete_item(
        Key={
            'username': username
        }
    )
    return {
        "statusCode": response['ResponseMetadata']['HTTPStatusCode']
    }

def _getTable(table_name):
    return _dynamodb.Table(table_name)

def _getParameters(body):
    parsed = urlparse.parse_qs(body)
    return (parsed['username'][0], parsed['githubUsername'][0])

def _getUsernameFromPath(event):
    return event['pathParameters']['username']

def _insert(item, table):
    return table.put_item (
                Item = item
            )   