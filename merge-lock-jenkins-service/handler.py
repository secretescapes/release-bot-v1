import boto3
import botocore
import logging
import json
import os
import sys
import urlparse

here = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(here, './vendored'))
sys.path.append(os.path.join(here, './commons'))
import requests
from jenkinsapi.jenkins import Jenkins
from commons import publish_to_sns

logger = logging.getLogger()
logger.setLevel(logging.INFO)

from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

stage = os.environ.get("STAGE")
region = os.environ.get("REGION")
account_id = os.environ.get("ACCOUNT_ID")

def pipelineTriggerFunction(event, context):
    logger.info("Pipeline Trigger function invoked with event: %s" % event)
    received_data = json.loads(event['Records'][0]['Sns']['Message'])
    queue = json.loads(received_data['queue'])
    if (len(queue) == 0):
        logger.warn("New Top Listener invoked with empty queue")
        return

    branch = queue[0]['branch']
    #TODO: Use params for this
    return_url = "https://gx23wyi7sl.execute-api.eu-west-1.amazonaws.com/dev/mergelock-jenkins/status"
    logger.info("Branch %s will be send to Jenkins" % branch)
    jenkins_client = Jenkins('http://jenkins.secretescapes.com:9090', 'mario.martinez@secretescapes.com', '40116ff0cc3575a7ee72e889b05effb3')
    jenkins_client['merge-to-master'].invoke(build_params={'BRANCH_TO_MERGE': branch, 'NOTIFICATION_ENDPOINT': return_url})
   
    return


def statusUpdateFunction(event, context):
	try:
		logger.info("Status Update function invoked with event: %s" % event)
		state = json.loads(event['body'])['state']
		outcome = json.loads(event['body'])['outcome']
		message = json.loads(event['body'])['message']
		branch = json.loads(event['body'])['branch']
		url = json.loads(event['body'])['url']

		logger.info("%s %s %s %s %s"% (state, outcome, message, branch, url))

		payload = {'state':state, 'branch': branch, 'url':url}
		publish_to_sns.publish(stage, "pipeline", account_id, region, payload)
	
	except Exception as e:
		logger.error(e)
	
	return {
                "statusCode": 200
            }
	