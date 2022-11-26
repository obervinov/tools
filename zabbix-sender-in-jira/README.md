# Zabbix sender in Jira
This script was created to add an alert method from zabbix to the Jira task manager.
When a trigger occurs:
1. zabbix calls the script by passing it data about the problem
2. the script creates a task in Jira based on the transmitted data

## Requirements
- [jira 3.4.1](https://pypi.org/project/jira/)

## Example
```sh
python3 zabbix-sender-in-jira.py --summary "Server server-1.example.com is down!" --description "No ping data within 1 minute" --components "zabbix"
```