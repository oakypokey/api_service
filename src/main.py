import os
from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from src.workday import wd_router, submit_praise, email_to_workerID
from src.slack import get_user_email, get_message
import re
from datetime import datetime

load_dotenv()

# Install the Slack app and get xoxb- token in advance
app = App(token=os.environ["SLACK_BOT_TOKEN"])
app_handler = SlackRequestHandler(app)

api = FastAPI()

api.include_router(wd_router)


# Add functionality here
@app.event("app_mention")
def handle_app_mentions(body, say, logger):
    logger.info(body)
    say("What's up?")


@app.message(re.compile("<@[^>]+>\s*\++"))
def respond_to_regex_match(message, say, context, ack):
    ack()

    matches = re.findall(r"<@[^>]+>\s*\++", message["text"])
    return_list = []
    yay_message = get_message(message["text"])
    from_username = get_user_email(message["user"])

    for match in matches:
        username = re.search(r"<@([^>]+)>", match)
        username = username.group(1)
        points = match.count("+")
        return_list.append(
            {
                "to_worker": username,
                "points": points,
                "feedback": yay_message,
                "from_worker": from_username,
                "feedback_date": datetime.now().strftime("%Y-%m-%d"),
            }
        )

    for item in return_list:
        item["to_worker"] = get_user_email(item["to_worker"])

    formed_items = email_to_workerID(return_list)
    formed_object = {"data": return_list}

    response = submit_praise(formed_object)

    print(response)

    say(f'Woohoo! :tada: Thanks for providing that feedback <@{message["user"]}>')


@app.event("message")
def handle_message(body, logger):
    # print(body)
    pass


@app.command("/requestfeedback")
def repeat_text(ack, respond, command):
    # Acknowledge command request
    ack()

    respond(f"{command['text']}")


@api.post("/slack/events")
async def endpoint(req: Request):
    try:
        body = await req.body()
        data = await req.json()
        if "challenge" in data:
            return {"challenge": data["challenge"]}
    except Exception as e:
        print("Something happened but we don't care...")

    return await app_handler.handle(req)
