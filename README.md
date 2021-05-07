# ml-serverless

This project is done using serverless framework (still in beta) https://serverless.com/. At the moment we have 6 different services, you can see how they are related here: https://docs.google.com/a/secretescapes.com/presentation/d/1FN3o_7-az8Eq2hGEguh6K6FsUci2xZjxKl0t2FqGMyY/edit?usp=sharing

You will need to have installed serverless, npm and pip.

The repository for this project is: https://github.com/secretescapes/ml-serverless

Before being able to deploy the services, you will need to configure an aws profile. Make sure when you configure it in your machine you name it `release-bot`. https://serverless.com/framework/docs/providers/aws/guide/credentials/

Now you can start deploying services. Make sure to follow this order the first time. This is because some of them need a reference to other, and this reference is not known until the service is created.

* `merge-lock-user-service`
* `merge-lock-github-service`
* `merge-lock-queue-service`
* `merge-lock-status-service`
* `slack-merge-lock-service`
* `merge-lock-notification-service`

Get into the service folder:
- first you will need to install dependencies `npm install` (note: ignore the warnings) after that, you should have a folder `node_modules`

- Now install python dependencies: `pip install -r  requirements.txt -t vendored/` this will create a folder vendored with the dependencies inside.

- Now is moment to deploy ` serverless deploy  --stage {dev|prod} --region {region} --profile {aws_profile} -v`. The parameter `--profile` is optional and by default it will use `release-bot`.

Once the service is deployed, you will see something like:
```
endpoints:
  POST - https://XXXXXXXXXXX.execute-api.eu-west-1.amazonaws.com/prod/github/push
```

For the following services `merge-lock-user-service` ,  `merge-lock-queue-service` and `merge-lock-status-service` You will need to copy the first part (between `https://` and `.execute...` and create a file called `env_vars.yml` in the root of the project with the following content:
DEV_USER_SERVICE_API_ID: xxxxxxxxxxxxx
DEV_QUEUE_SERVICE_API_ID: xxxxxxxxxxxxxxxxxxx
DEV_STATUS_SERVICE_API_ID: xxxxxxxxxx
DEV_SLACK_TOKEN: xxxxxxxxxxx

PROD_USER_SERVICE_API_ID: xxxxxxxx
PROD_QUEUE_SERVICE_API_ID: xxxxxxxx
PROD_STATUS_SERVICE_API_ID: xxxxxxxxxxx
PROD_SLACK_TOKEN: xxxxxxxxxxx

ACCOUNT_ID: xxxxxxx

DEV_SLACK_WEBHOOK_URL: xxxxxxxxxxxxx
PROD_SLACK_WEBHOOK_URL: xxxxxxxxxxxxx

You can find `ACCOUNT_ID` value in the output of any service's deployment. It will be the firth element of any arn. For example ` merge-lock-queue-service-prod-back: arn:aws:lambda:eu-west-1:yyyyyyyyyyy:function:merge-lock-queue-service-prod-back` .

You might not need all of them, only the two related to the environment you are deploying.

Before deploying `merge-lock-queue-service` make sure you have in that file `{env}_USER_SERVICE_API_ID` with the appropriate value. Once you have deployed `merge-lock-queue-service`, fill `{env}_QUEUE_SERVICE_API_ID` before deploying the other two services.

Now that all the services has been deployed and linked between them, you will need to configure the github webhook and the slack custom command.

Go to the github repository you want to set up, go to settings > Webhooks and create a new one. In the payload URL enter the url for the github service. Leave "Just the push event." checked. Make sure you select application/json as content type. (Note: at the moment we don't need to add a secret, but this might change in the future).

Now, login in slack and go https://<slack-team-url>.com/apps/build/custom-integration and click "Slash command". Fill the fields making sure URL is set to the url given by the service `slack-merge-lock-service` and make note of the token. You will need to paste the token into the `env_vars.yml` file like `DEV_SLACK_TOKEN` or `PROD_SLACK_TOKEN`.

Go back to slack and configure a new webhook. Copy the url and add a new variable inside (depending on the envaironment, prod or dev) env_vars.yml:

DEV_SLACK_WEBHOOK_URL: xxxxxxxxxxxxxxx
PROD_SLACK_WEBHOOK_URL: yyyyyyyyyyyyyyy

