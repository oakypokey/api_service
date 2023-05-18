from dotenv import load_dotenv
from slack_sdk import WebClient
from fastapi import APIRouter, Depends, Query
from fastapi.responses import HTMLResponse
from typing import Annotated

import os
from src.dependencies import get_token_header

scopes = [
    'chat:write',
    'channels:read',
    'app_mentions:read'
]

if(os.environ.get('ENV') == 'dev'):
    URL_STUB = "http://localhost:8080"
else:
    URL_STUB = "https://apiservice-growthcopilot.b4a.run"

load_dotenv()

SLACK_CLIENT = WebClient()

router = APIRouter(prefix="/slack",
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not a valid endpoint"}}
)

@router.get("/install")
def pre_install():
    url = URL_STUB + '/slack/oauth_redirect'
    state = "12345"
    scope_string = '&amp;'.join(scopes)
    print(scope_string)
    return HTMLResponse('<html><a href="https://slack.com/oauth/v2/authorize?' \
        f'scope={scope_string}&client_id={os.environ.get("SLACK_CLIENT_ID")}&state={state}&redirect_uri={url}">' \
        'Add to Slack</a></html>')


@router.get("/oauth_redirect")
def post_install(code: str | None, state: str | None ):
    # Verify the "state" parameter

    # Request the auth tokens from Slack
    response = SLACK_CLIENT.oauth_v2_access(
        client_id=os.get.environ("SLACK_CLIENT_ID"),
        client_secret=os.get.environ("SLACK_CLIENT_SECRET"),
        code=code
    )
    print(response)

    # Save the bot token to an environmental variable or to your data store
    # for later use
    os.environ["SLACK_BOT_TOKEN"] = response['access_token']

    # Don't forget to let the user know that OAuth has succeeded!
    return "Installation is completed!"

@router.post("/cheer")
def assign_cheer():
    return "cheer!"