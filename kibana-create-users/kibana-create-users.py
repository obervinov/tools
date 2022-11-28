#!/usr/bin/env python

# Import vars from variables.py
import variables
import requests
import re
import string
import random
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from jsonpath_ng import parse


# Load vars #
roles = variables.roles_ps
es_username = variables.es_user
es_password = variables.es_password
es_url = variables.es_url

SLACK_BOT_TOKEN = "****"
SLACK_TEXT_HEAD = (
        "Hello there! :wave:\n"
        "This is a personal account for accessing kibana\n"
        "If any access rights are missing, please contact me <@o.bervinov>\n\n"
        "Your Login/Password:"
)


def slack_send_message(email, creds):
    client = WebClient(token=SLACK_BOT_TOKEN)

    try:
        slack_user_response = client.users_lookupByEmail(email=email)
    except SlackApiError as e:
        print(email)
        print(e.response['error'])

    jsonpath_expression = parse('$.user.id')
    slack_user_id = jsonpath_expression.find(slack_user_response)
    slack_user_id = "@" + str(slack_user_id[0].value)

    try:
        client.chat_postMessage(channel=slack_user_id, text=SLACK_TEXT_HEAD + creds)
        print("send slack success")
    except SlackApiError as e:
        assert e.response["ok"] is False
        assert e.response["error"]
        print(f"Got an error: {e.response['error']}")


def passwd_gen(size=12, chars=string.ascii_uppercase + string.digits + string.ascii_lowercase):
    return ''.join(random.choice(chars) for _ in range(size))


def user_data_gen(email):
    # Email filters by @domain
    if re.search('@example.com', email) or re.search('@example2.com', email):
        user = email.split("@")

        username = user[0].split(".")
        array_len = len(username)

        if array_len > 1:
            username = username[0][:1] + "." + username[1]

            username_full = user[0].split(".")
            full_name_1 = username_full[0][:1].upper() + username_full[0][1:]
            full_name_2 = username_full[1][:1].upper() + username_full[1][1:]
        else:
            username = username[0]
            full_name_1 = username[0]
            full_name_2 = ''

        password = passwd_gen()
        link = es_url + username

        response = requests.post(
                                link,
                                auth=(
                                        es_username,
                                        es_password
                                      ),
                                headers={
                                            'Content-Type': 'application/json'
                                        },
                                json={
                                        "password": password,
                                        "full_name": f"{full_name_1} {full_name_2}",
                                        "email": email,
                                        "roles": roles,
                                        "metadata": {}
                                    }
                            )

        print("create user " + str(response))
        CREDENTINALS = f"\n `{username}`\n`{password}`"
        return CREDENTINALS

    else:
        user = email.split("@")

        username = user[0]
        username_full = username
        password = passwd_gen()
        link = es_url + username
        enabled = 'true'

        response = requests.post(
                                link,
                                auth=(
                                        es_username,
                                        es_password
                                     ),
                                headers={
                                            'Content-Type': 'application/json'
                                        },
                                json={
                                        "password": password,
                                        "full_name": username_full,
                                        "email": email,
                                        "roles": roles,
                                        "metadata": {},
                                        "enabled": enabled
                                    }
                            )

        print("create user " + str(response))
        CREDENTINALS = f"\n `{username}`\n`{password}`"
        return CREDENTINALS


file = open("new_users_kibana.list", "r")
lines = file.readlines()
for line in lines:
    line = re.sub("^\s+|\n|\r|\s+$", '', line)
    creds = user_data_gen(line)
    slack_send_message(line, creds)
file.close
print('done')
