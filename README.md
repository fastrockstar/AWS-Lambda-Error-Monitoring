# AWS-Lambda-Error-Monitoring
This repo contains an AWS Error Lambda Monitoring.

It creates an infrastructure, which hanldes error occuring during the execution of Lambda functions.

If an error occured, an error log is created. This will trigger a function that creates a CSV file, that is saved in an S3 bucket.

Also the error message will be sent via email and a Slack message.
