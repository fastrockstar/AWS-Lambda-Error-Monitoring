from aws_cdk import (
    aws_cloudwatch as cw,
    aws_lambda as _lambda,
    aws_s3 as s3,
    aws_s3_notifications as s3_notifications,
    aws_sns as sns,
    aws_sns_subscriptions as sns_subscriptions,
    core
)
import aws_cdk.aws_iam as iam


class LambdaMonitoringStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, lambda_func: _lambda.Function, bucket_name: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create an S3 bucket to store the CSV file
        bucket = s3.Bucket(self, "ErrorLogBucket", bucket_name=bucket_name)

        # Grant the Lambda function permission to write to the bucket
        bucket.grant_write(lambda_func)

        # Create a Log Group for the Lambda function
        log_group = cw.LogGroup(self, "LogGroup", log_group_name=f"/aws/lambda/{lambda_func.function_name}")

        # Create a metric filter to track error logs
        error_metric_filter = log_group.add_metric_filter(
            "ErrorMetricFilter",
            filter_pattern=cw.FilterPattern.all_terms("ERROR", lambda_func.function_name),
            metric_name="LambdaFunctionErrorCount",
            metric_namespace="Custom/Lambda"
        )

        # Create a CloudWatch Alarm to monitor error metric
        alarm = cw.Alarm(
            self, "ErrorAlarm",
            metric=error_metric_filter.metric(),
            evaluation_periods=1,
            threshold=1,
            comparison_operator=cw.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
            alarm_description="Alarm for Lambda function errors"
        )

        # Create an SNS topic to receive alarm notifications
        topic = sns.Topic(self, "ErrorTopic")
        
        # Add an email subscription to the SNS topic
        email_subscription = sns_subscriptions.EmailSubscription("your-email@example.com")
        topic.add_subscription(email_subscription)

        # Add an action to the alarm to publish to the SNS topic
        alarm.add_alarm_action(cw.SnsAction(topic))

        # Create a Lambda function to export error logs to S3
        export_function = _lambda.Function(
            self, "ExportFunction",
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler="index.handler",
            code=_lambda.Code.from_asset("lambda_export_function"),
            environment={
                "BUCKET_NAME": bucket.bucket_name,
                "LOG_GROUP_NAME": log_group.log_group_name,
            },
            role=iam.Role.from_role_arn(
                self, "Role", role_arn=lambda_func.role.role_arn,
            ),
        )

        # Grant the export function permission to read from the Log Group
        log_group.grant_read(export_function)

        # Configure the S3 bucket to trigger the export function when a new object is created
        bucket.add_object_created_notification(
            s3_notifications.LambdaDestination(export_function)
        )

app = core.App()
lambda_func = _lambda.Function(self, "MyFunction",
                                runtime=_lambda.Runtime.PYTHON_3_8,
                                handler="index.handler",
                                code=_lambda.Code.from_asset("lambda_function"))

LambdaMonitoringStack(app, "LambdaMonitoringStack", lambda_func, bucket_name="my-bucket")

app.synth()
