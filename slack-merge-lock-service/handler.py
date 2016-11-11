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

def merge_lock(event, context):
    try:
        params = event.get('body')
        text = params.get('text').split()
        logger.info("Command received: %s" % text)

        if len(text) == 1 and text[0].lower() == 'list':
            return {"text":_list_request_handler()}

        elif len(text) == 2 and text[0].lower() == 'add':
            username = text[1]
            return {"text":_add_request_handler(username)}

        elif len(text) == 2 and text[0].lower() == 'remove':
            username = text[1]
            return {"text":_remove_request_handler(username)}
        elif len(text) == 3 and text[0].lower() == 'register':    
            username = text[1]
            githubUsername = text[2]
            return {"text":_register_request_handler(username, githubUsername)}
        else:
            return {"text": "unrecognized command, please try one of these:\n/lock list\n/lock add [username]\n/lock remove [username]\n/lock register [username] [github username]"}
    except Exception as e:
        logger.error(e)
        return {"text": "Something went really wrong, sorry"}

def _register_request_handler(username, githubUsername):
    #TODO: HARDCODED URL!!
    response = requests.put("https://r9mnwy3vfi.execute-api.eu-west-1.amazonaws.com/dev/user-service/user", data={'username': username, 'githubUsername':githubUsername})
    if response.status_code == 200:
        return '%s has been *registered* with the github username %s' % (username, githubUsername)
    else:   
        logger.error("Status code receive: %i" % response.status_code)   
        return 'Something went wrong, please try again'

def _remove_request_handler(username):
    #TODO: HARDCODED URL!!
    response = requests.post("https://5ywhqv93l9.execute-api.eu-west-1.amazonaws.com/dev/mergelock/remove", data={'username': username})
    if response.status_code == 200:
        return '%s has been *removed* from the queue' % username
    elif response.status_code == 401:
        return '%s is not in the queue' % username
    else:
        logger.error("Status code receive: %i" % response.status_code)   
        return 'Something went wrong, please try again'

    return response.text

def _add_request_handler(username):
    #TODO: HARDCODED URL!!
    response = requests.post("https://5ywhqv93l9.execute-api.eu-west-1.amazonaws.com/dev/mergelock/add", data={'username': username})
    logger.info ("Status code: %d" % response.status_code)
    if response.status_code == 200:
        return '%s has been *added* to the queue' % username
    elif response.status_code == 401:
        return '%s *was already* in the queue' % username
    else:
        logger.error("Status code receive: %i" % response.status_code)   
        return 'Something went wrong, please try again'

def _list_request_handler():
    #TODO: HARDCODED URL!!
    response = requests.get("https://5ywhqv93l9.execute-api.eu-west-1.amazonaws.com/dev/mergelock/list")
    if response.status_code == 200:
        return _format_successful_list_response(response.json()['queue'])
    else:
        logger.error("Status code received: %i" % response.status_code)
        logger.error("Error received: %i" % response.json()['queue'])
        return {'text': 'Something went wrong, please try again'}

def _format_successful_list_response(json):
    i = 1
    text = 'Here is the current status of the queue:\n'
    for item in json:
        if i == 1:
            text += "*%d. %s*\n" % (i, item['username'])
        else:
            text += "%d. %s\n" % (i, item['username'])
        i+= 1
    
    if i == 1:
        text = 'The queue is currently empty!'
    return text