from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
import os
import re

load_dotenv()

slack_client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))


def get_user_email(user_id):
    try:
        # Call the users.info API to retrieve user details
        response = slack_client.users_info(user=user_id)

        # Extract the email from the response
        user_email = response["user"]["profile"]["email"]

        return user_email

    except SlackApiError as e:
        # Handle API errors
        print(f"Error: {e.response['error']}")


def get_message(message_input):
    username_pattern = r"<@[^>]+>"

    # Find the last occurrence of the username pattern
    last_username_match = None
    for match in re.finditer(username_pattern, message_input):
        last_username_match = match

    # Extract the message portion after the last set of pluses
    if last_username_match:
        message_start_index = last_username_match.end()
        message = message_input[message_start_index:].strip()
        message = re.sub(r"\++\s*", "", message)
        return message

    return ""
