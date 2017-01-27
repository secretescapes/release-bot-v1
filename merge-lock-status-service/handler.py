import json
import boto3
import os
import logging
import time

stage = os.environ.get("STAGE")
region = os.environ.get("REGION")

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def open(event, context):
    logger.info("Invoked open with event: %s" % event)
    try:
        _insert_status_event("OPEN")
    except Exception as e: 
        logger.error("Exception: %s" % e)
        return _responseError(500, "Unknown error")

    return {
        "statusCode": 200
    }

def close(event, context):
    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response

def list(event, context):
    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response


def _insert_status_event(event):
    table = _getTable('statusEvent')
    return table.put_item(
        Item = {
        'type': event,
        'timestamp': int(round(time.time() * 1000))
        }
    )

def _responseError(status_code, error_msg):
    return {
            "statusCode": status_code,
            "body": '{"error": "%s"}' % error_msg
        }

def _getTable(table_name):
    dynamodb = boto3.resource('dynamodb', region_name=region)
    return dynamodb.Table("%s-%s" %(table_name, stage))