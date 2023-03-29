from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

class SlackNotifier:
    def __init__(self, slack_token, slack_channel):
        """
        Initializes a new instance of the SlackNotifier class.

        :param slack_token: The Slack API token.
        :param slack_channel: The name or ID of the Slack channel to post messages to.
        """
        self.slack_token = slack_token
        self.slack_channel = slack_channel

    def send_message(self, message, log_group_name=None):
        """
        Sends a message to the configured Slack channel.

        :param message: The message to send.
        :param log_group_name: The name of the CloudWatch Logs group containing the error log (optional).
        """
        # Initialize a new Slack API client with the provided token.
        client = WebClient(token=self.slack_token)

        # If a log group name is provided, generate a Log group button for the Slack message.
        if log_group_name:
            # Construct the URL for the Log group in the AWS Management Console.
            log_group_url = f"https://console.aws.amazon.com/cloudwatch/home?region={self.region}#logsV2:log-groups/log-group/{log_group_name}"
            # Construct the attachment for the Slack message, containing the error message and the Log group button.
            log_group_button = {
                "type": "button",
                "text": "View logs in CloudWatch",
                "url": log_group_url
            }
            attachments = [{
                "color": "#ff0000",
                "title": "Error Log",
                "text": message,
                "actions": [log_group_button]
            }]
            message = ""  # Clear the message body if an attachment is included.
        else:
            attachments = None

        try:
            # Use the Slack API client to post a message to the configured channel.
            response = client.chat_postMessage(
                channel=self.slack_channel,
                text=message,
                attachments=attachments
            )
            return response["ts"]
        except SlackApiError as e:
            print("Error sending message: {}".format(e))
