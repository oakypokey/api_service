import json
from dataclasses import dataclass, field

from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, Response, Depends

from .dependencies import get_query_token, get_token_header
from .routers import slack_bot

app = FastAPI()
app.include_router(slack_bot.router)

@app.get("/")
def read_root() -> Response:
    return Response("The server is running!")


