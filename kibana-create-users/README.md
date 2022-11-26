# Creating users in kibana and sending credentials to slack
This script is designed for automated creation of users in kibana by email list and sending credentials for access to slack

## Requirements
- [slack-sdk 3.19.4](https://pypi.org/project/slack_sdk/)
- Email formats: `oleg.bervinov@example.com`
- Added emails in [new_users_kibana.list](new_users_kibana.list)
- Install settings in [variables.py](variables.py)

## Example
```sh
# Specify the number of days for unloading
python3 kibana-create-users.py
```