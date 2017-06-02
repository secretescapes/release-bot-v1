import logging
import json
import os
import sys

here = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(here, './vendored'))
sys.path.append(os.path.join(here, './commons'))
from commons import publish_to_sns

logger = logging.getLogger()
logger.setLevel(logging.INFO)

from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

import requests

stage = os.environ.get("STAGE")
region = os.environ.get("REGION")
account_id = os.environ.get("ACCOUNT_ID")
JENKINS_SERVICE_API_ID = os.environ.get("%s_JENKINS_SERVICE_API_ID" % stage.upper())

JENKINS_URL = os.environ.get("%s_JENKINS_URL" % stage.upper())
JENKINS_TOKEN = os.environ.get("%s_JENKINS_TOKEN" % stage.upper())


def pipelineTriggerFunction(event, context):
    logger.info("Pipeline Trigger function invoked with event: %s" % event)
    received_data = json.loads(event['Records'][0]['Sns']['Message'])
    queue = json.loads(received_data['queue'])
    if (len(queue) == 0):
        logger.warn("New Top Listener invoked with empty queue")
        return

    branch = queue[0]['branch']
    return_url = "https://%s.execute-api.eu-west-1.amazonaws.com/%s/mergelock-jenkins/status" % (JENKINS_SERVICE_API_ID, stage)
    logger.info("Branch %s will be send to Jenkins" % branch)
    requests.post("%s/buildByToken/buildWithParameters?token=%s&job=merge-to-master"%(JENKINS_URL, JENKINS_TOKEN), data={'BRANCH_TO_MERGE': branch, 'NOTIFICATION_ENDPOINT': return_url})
    return


def statusUpdateFunction(event, context):
	try:
		logger.info("Status Update function invoked with event: %s" % event)
		state = json.loads(event['body'])['state']
		branch = json.loads(event['body'])['branch']
		url = json.loads(event['body'])['url']

		logger.info("%s %s %s" % (state, branch, url))

		payload = _create_message_payload(state, branch, url)
		if payload:
			publish_to_sns.publish(stage, "pipeline", account_id, region, payload)
	
	except Exception as e:
		logger.error(e)
	
	return {
		"statusCode": 200
	}


def _create_message_payload(state, branch, url):
	if state == 'START':
		message = "Merging master."
	elif state == 'FAILURE_MERGE':
		message = "Merge failed."
	elif state == 'START_TEST':
		message = "Merge successful."
	elif state == 'FAILURE_TEST':
		message = "Test failures."
	elif state == 'SUCCESS':
		message = "Tests successful."
	elif state == 'FAILURE_ABNORMAL':
		message = "The job was stopped due to an unexpected failure."

	positive = 'FAILURE' not in state
	return {
		"attachments": [
			{
				"title": ":lock: <{0}|{1}>".format(url, branch),
				"text": message,
				"color": "danger" if "FAILURE" in state else "good" if state == "SUCCESS" else None
			}
		]
	}
