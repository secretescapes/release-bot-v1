import json
import logging
import os
import sys


here = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(here, './vendored'))
import requests

from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

stage = os.environ.get("STAGE")

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def push(event, context):
    try:
        params = json.loads(event.get('body'))
        branch_name = params['ref']
        author_username = params['pusher']['name']
        logger.info("Push invoked for branch %s, by author %s" % (branch_name, author_username))

        if branch_name == 'refs/heads/master':
            #TODO: Hardcoded url
            response = requests.get("https://r9mnwy3vfi.execute-api.eu-west-1.amazonaws.com/%s/user-service/user/reverse/%s" % (stage, author_username))
            if response.status_code == 200:
                username = response.json()[0]['username']
                #TODO: Hardcoded url
                response = requests.get("https://5ywhqv93l9.execute-api.eu-west-1.amazonaws.com/%s/mergelock/pop/%s" % (stage, username))
                if response.status_code == 400:
                    logger.info("[%s:%s] was not at the top of the queue" % (author_username, username))
                elif response.status_code == 200:
                    logger.info("[%s:%s] was at the top of the queue and has been removed" % (author_username, username))
        return {
            "statusCode": 200
        }
    except Exception as e:
        logging.exception(e)
        return {
            "statusCode": 500
        }
