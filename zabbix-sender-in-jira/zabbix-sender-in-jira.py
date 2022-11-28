#!/usr/bin/env python3

import argparse
import logging
from jira import JIRA


# INPUT ARGS #
parser = argparse.ArgumentParser()
parser.add_argument('--summary', type=str, default='null')
parser.add_argument('--description', type=str, default='null')
parser.add_argument('--components', type=str, default='null')
args = parser.parse_args()
summary = args.summary
description = args.description
components = args.components


# ENV #
logging.basicConfig(level=logging.DEBUG)
link = "https://jira-cloud.net"
project = "SD"
user = "o.bervinov@example.com"
token = "***"
issuetype = "Request"
issue_dict = {'project': {'key': project},
              'summary': summary,
              'description': description,
              'issuetype': {'name': issuetype},
              'components': [{'name': components}]
              }


def create_issue(LINK, USER, PASS):
    jira_options = {'server': LINK}
    jira = JIRA(options=jira_options, basic_auth=(USER, PASS))
    issue = jira.create_issue(fields=issue_dict)
    return issue


issue = create_issue(link, user, token, issue_dict)
print(issue)
