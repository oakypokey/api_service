import json
from dataclasses import dataclass, field
from slack_bolt.adapter.socket_mode import SocketModeHandler

from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, Response, Depends

from src.dependencies import get_query_token, get_token_header
from src.routers import slack_bot

app = FastAPI()

@app.get("/")
def read_root() -> Response:
    return Response("The server is running!")

if __name__ == "__main__":
    SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN")).start()


