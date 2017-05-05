
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def pipelineTriggerFunction(event, context):
    logger.info("Pipeline Trigger function invoked with event: %s" % event)

    return
