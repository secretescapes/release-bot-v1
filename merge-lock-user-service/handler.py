import json

def create(event, context):
    body = {
        "message": "CREATE",
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    };

    return response

    # Use this code if you don't use the http event with the LAMBDA-PROXY integration
    """
    return {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "event": event
    }
    """

def list_all(event, context):
    body = {
        "message": "LIST ALL",
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    };

    return response

    # Use this code if you don't use the http event with the LAMBDA-PROXY integration
    """
    return {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "event": event
    }
    """

def list(event, context):
    body = {
        "message": "LIST",
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    };

    return response

    # Use this code if you don't use the http event with the LAMBDA-PROXY integration
    """
    return {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "event": event
    }
    """
def delete(event, context):
    body = {
        "message": "DELETE",
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    };

    return response

    # Use this code if you don't use the http event with the LAMBDA-PROXY integration
    """
    return {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "event": event
    }
    """