from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


class SlackNotifier:
    def __init__(self, slack_token: str, slack_channel: str):
        self.slack_client = WebClient(token=slack_token)
        self.slack_channel = slack_channel
    
    def send_message(self, message: str):
        try:
            response = self.slack_client.chat_postMessage(channel=self.slack_channel, text=message)
            print(f"Sent message: {message}")
        except SlackApiError as e:
            print(f"Error sending message: {e}")
