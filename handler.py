from aws_cdk import (
    aws_lambda as _lambda,
    aws_s3 as s3,
    aws_logs as logs,
    aws_iam as iam,
    core
)
from os import getenv
import csv
import io

def handler(event, context):
    s3_resource = boto3.resource('s3')
    bucket_name = getenv('BUCKET_NAME')
    log_group_name = getenv('LOG_GROUP_NAME')

    logs_client = boto3.client('logs')
    response = logs_client.describe_log_streams(logGroupName=log_group_name, orderBy='LastEventTime', descending=True, limit=1)
    log_stream_name = response['logStreams'][0]['logStreamName']

    log_events = logs_client.get_log_events(
        logGroupName=log_group_name,
        logStreamName=log_stream_name
    )

    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)

    writer.writerow(["Timestamp", "Message"])
    for event in log_events['events']:
        timestamp = event['timestamp']
        message = event['message']
        writer.writerow([timestamp, message])

    s3_resource.Object(bucket_name, f"{log_stream_name}.csv").put(Body=csv_buffer.getvalue())
