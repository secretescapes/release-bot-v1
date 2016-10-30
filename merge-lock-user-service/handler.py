import json
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

_client = boto3.client('dynamodb')
_dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')

def update(event, context):
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
                "errorMsg": "Database error"
            }

    except KeyError as key:
        logger.error("Missing key: %s" % key)
        return {
            "statusCode": 400,
            "errorMsg": "Malformed Request"
        }
   

def list_all(event, context):
    return {
        "message": "List all",
        "event": event
    }

def list(event, context):
    
    return {
        "message": "List",
        "event": event
    }
    
def delete(event, context):
    return {
        "message": "Delete",
        "event": event
    }

def _getTable(table_name):
    return _dynamodb.Table(table_name)

def _getParameters(body):
    return (body['username'], body['githubUsername'])

def _insert(item, table):
    return table.put_item (
                Item = item
            )   