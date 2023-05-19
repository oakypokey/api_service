import base64
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from oauthlib.oauth2 import WebApplicationClient
import os
import requests
from dotenv import load_dotenv
import urllib.parse

load_dotenv()


# wd_client = WebApplicationClient(os.environ.get("WEX_API_CLIENT_ID"))
class wd_client:
    access_token = "eyJhbGciOiJSUzUxMiIsImtpZCI6IjIwMjMtMDUtMTkifQ.eyJpc3MiOiJDXHUwMDNkVVMsU1RcdTAwM2RDQSxMXHUwMDNkUGxlYXNhbnRvbixPVVx1MDAzZERldmVsb3BtZW50LE9cdTAwM2RXb3JrZGF5LENOXHUwMDNkT0NUT1BBQVMiLCJhdXRoX3RpbWUiOjE2ODQ0OTE2MzksImF1dGhfdHlwZSI6IlBhYVMiLCJzeXNfYWNjdF90eXAiOiJOIiwic2NvcGUiOnsicmVnaW9uX2ZxZG4iOiJhcGkud29ya2RheS5jb20iLCJyZWdpb24iOiJhd3M6dXMtd2VzdC0yIiwiY2xpZW50X2lkIjoiTkRVMFltVTNZV1V0TldVNFppMDBNMk00TFdJMk9EY3RZVEV3TXpZME5qQTVNek5oIn0sInRva2VuVHlwZSI6IklkZW50aXR5Iiwic3ViIjoibG1jbmVpbCIsImF1ZCI6IndkIiwiZXhwIjoxNjg0NDk1MjM5LCJpYXQiOjE2ODQ0OTE2MzksImp0aSI6Ingxb3RmcXFxdnh1YWViazZjcGE1a215bDBhbTRhYWt3a25naGQ5YjE3dWJubXpnY2giLCJ0ZW5hbnQiOiJoYWNrMTdfd2NwZGV2MSJ9.kklfPY2RltsSVZmdW-Ijq0LUQcErwHTeUAcLPNNkbYotyKERsE113rYWcZwwLTWuh1F5EZfZ6ykf-2zBzautO9CYLCxpm0a5ZedzmehKZNDQGs5wSmPKLndB5KZ06WrUbtBpGJy9EYJjYS9r0v0rsdVFSFBB1dS6cAGTpM4JtHXGUfoi6cvyRwK2ZIunm21zp5WPoq8DdfMUMWuD527j5HP7KAfHpSBgy_h-xhzugbkwOlMLXieUrbqUZvIpWSNg8-ZngoJiArZTdLG9NDgrR3biPA8fIqbJR2c1Udem175QOWhv5tJ6y8nWeVQAeMOFc8TDyywmgfSe9qBcN6PkFA"


wd_router = APIRouter(prefix="/wd")


@wd_router.get("/login")
def login():
    url = wd_client.prepare_request_uri(
        "https://auth.api.workday.com/v1/authorize",
        redirect_uri=os.environ.get("APP_URL_STUB") + "wd/oauth_redirect",
        scope=[],
        state="",
    )
    return HTMLResponse(f"<a href={url}> Login to Workday </a>")


@wd_router.get("/oauth_redirect")
def oauth_redirect(request: Request):
    wd_client = WebApplicationClient(os.environ.get("WEX_API_CLIENT_ID"))
    print(request.query_params.get("code"))

    CLIENT_ID = os.environ.get("WEX_API_CLIENT_ID")
    CLIENT_SECRET = os.environ.get("WEX_API_CLIENT_SECRET")
    STRING1 = (CLIENT_ID + ":" + CLIENT_SECRET).encode("utf-8")
    print(STRING1)

    BASIC_AUTH_STRING = base64.b64encode(STRING1).decode("utf-8")

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Basic " + BASIC_AUTH_STRING,
    }

    data = wd_client.prepare_request_body(
        code=request.query_params.get("code"),
        redirect_uri=os.environ.get("APP_URL_STUB") + "wd/oauth_redirect",
        client_id=os.environ.get("WEX_API_CLIENT_ID"),
        client_secret=os.environ.get("WEX_API_CLIENT_SECRET"),
    )

    print(data)
    response = requests.post(
        "https://auth.api.workday.com/v1/token", data=data, headers=headers
    )

    print(response.text)
    wd_client.parse_request_body_response(response.text)

    return "Success!"


def submit_praise(payload):
    print(payload)
    headers = {
        "Authorization": "Bearer " + wd_client.access_token,
        "Content-Type": "application/json",
    }
    response = requests.post(
        "https://api.workday.com/orchestrate/v1/apps/sensAI_ycgvyt/orchestrations/postFeedbackAnalysisAsync/launch",
        headers=headers,
        json=payload,
    )
    return response


def email_to_workerID(items):
    result = items
    headers = {"Authorization": "Bearer " + wd_client.access_token}
    list_items = [f'"{item["to_worker"]}"' for item in items]
    list_items.append(f'"{items[0]["from_worker"]}"')

    formatted_string = ", ".join(list_items)
    wql = f"SELECT workdayID, email_PrimaryWork FROM workersForHCMReporting (dataSourceFilter = allActiveWorkers) WHERE email_PrimaryWork in ({formatted_string})"
    response = requests.get(
        f"https://api.workday.com/wql/v1/data?query={urllib.parse.quote_plus(wql)}",
        headers=headers,
    )

    wid_email_list = response.json()
    wid_email_list = wid_email_list["data"]
    wid_email_map = {}

    for email in wid_email_list:
        wid_email_map[email["email_PrimaryWork"]] = email["workdayID"]

    for key in result:
        key["to_worker"] = wid_email_map[key["to_worker"].lower()]
        key["from_worker"] = wid_email_map[key["from_worker"].lower()]

    return result
