#!/usr/bin/env python3
# import logging
import json
import re
import sys
import argparse
from jsonpath_ng import parse
from kubernetes import client, config

# ENV #
# logging.basicConfig(level=logging.DEBUG)

config.load_kube_config(config_file='~/.kube/config')
ns_array = ['ns-1', 'ns-2']


# INPUT ARGS #
parser = argparse.ArgumentParser()
parser.add_argument('--action', type=str, default='null')
parser.add_argument('--item', type=str, default='null')
args = parser.parse_args()
input_action = args.action
input_item = args.item


# GET PODS AND CONTAINERS NAME ITEMS #
# ex. POD:logstash-0/CONTAINER:logstash
def get_containers(namespace):
    v1 = client.CoreV1Api()
    pod_list = v1.list_namespaced_pod(namespace)
    pods = []
    for pod in pod_list.items:
        # This block removes all values that the json-validator might break
        containers = str(pod.spec.containers).replace("'", '"').replace("\n", "").replace(" ", "")
        containers = containers.replace("None", '"None"').replace(":True", ':"True"').replace(":False", ':"False"')
        containers = re.sub(r'"args":\[".+"\],"command":\["/bin/sh","-c"\],', '', containers)
        containers = re.sub(r',"value":"Basic""\w+=="', '', containers)
        containers = re.sub(r'"args":\[".text.+\],"command":"None",', '', containers)
        containers = re.sub(r'"_exec":{"command":\["/bin/sh",.+"get/foo"\]},', '', containers)
        containers = re.sub(r'"env":\[{.+"value_from":"None"}\],"env_from":"None",', '', containers)
        containers = re.sub(r'{"post_start":{"_exec":{"command":\["/bin/sh".+"pre_stop":"None"}', '""', containers)
        containers = json.loads(containers)

        for container in containers:
            jsonpath_expression = parse('$.[name]')

            try:
                containers_describe_json = jsonpath_expression.find(container)[0].value
            except Exception:
                containers_describe_json = str(jsonpath_expression.find(container))

            pods_containers = "POD:"+pod.metadata.name+"/"+"CONTAINER:"+containers_describe_json
            pods.append(pods_containers)
    return pods


# NAMSPACES RECURSIVE GET PODS_CONTAINERS #
# ex. NS:namespace-1/POD:pod-0/CONTAINER:container-0
def get_ns_pods_containers():
    json_ns_pods_containers = []

    for ns in ns_array:
        pods_containers_list = get_containers(ns)

        for pods_containers in pods_containers_list:
            value = "NS:"+ns+"/"+pods_containers
            json_key_value = {"{#NS_POD_CONTAINER}": value}
            json_ns_pods_containers.append(json_key_value)
            lld_json_ns_pods_containers = json.dumps({"data": json_ns_pods_containers})

    print(lld_json_ns_pods_containers)


# GET CONTAINER ALL METRICS JSON #
def get_container_metrics(namespace, pod_name, container_name):
    json_metrics = []

    json_key_value_phase = {"PHASE": get_container_phase(namespace, pod_name, container_name)}
    json_metrics.append(json_key_value_phase)
    json_key_value_restart_count = {"RESTART_COUNT": get_container_restart_count(namespace, pod_name, container_name)}
    json_metrics.append(json_key_value_restart_count)
    json_key_value_last_state_terminated = {"TERMINATED_REASON": get_container_last_state_terminated(
                                                                    namespace,
                                                                    pod_name,
                                                                    container_name
                                                                )}
    json_metrics.append(json_key_value_last_state_terminated)

    json_array_metrics = json.dumps({"metrics": json_metrics})
    print(json_array_metrics)


# CONTAINER STATUS PHASE #
def get_container_phase(namespace, pod_name, container_name):
    v1 = client.CoreV1Api()
    pod_list = v1.list_namespaced_pod(namespace)

    for pod in pod_list.items:
        pod_metadata_name = pod.metadata.name

        if pod_metadata_name == pod_name:
            pod_status = str(pod.status).replace("'", '"').replace("\n", "").replace(" ", "")
            pod_status = pod_status.replace("None", '"None"').replace(":True", ':"True"').replace(":False", ':"False"')
            pod_status = re.sub(
                            r'datetime\.datetime\(\d+,\d+,\d+,\d+,\d+,\d+,tzinfo\=tzutc\(\)\)',
                            '"None"',
                            pod_status
                        )
            try:
                pod_status = json.loads(pod_status)
            except Exception:
                pod_status = re.sub(
                                r'"message":"containerswithunreadystatus:\[\w+""(\w+|\w+-\w+)\]"',
                                '"message":"containerswithunreadystatus"',
                                pod_status
                            )
                try:
                    pod_status = json.loads(pod_status)
                except Exception:
                    print(pod_status)
                    sys.exit(1)

            jsonpath_expression = parse('$.[container_statuses]')
            pod_container_statuses = jsonpath_expression.find(pod_status)[0].value

            for container_info in pod_container_statuses:
                jsonpath_expression = parse('$.name')
                pod_container_statuses_name = jsonpath_expression.find(container_info)[0].value

                if pod_container_statuses_name == container_name:
                    jsonpath_expression_running = parse('$.state.running')
                    jsonpath_expression_terminated = parse('$.state.terminated')
                    jsonpath_expression_waiting = parse('$.state.waiting')

                    state_running = jsonpath_expression_running.find(container_info)[0].value
                    state_terminated = jsonpath_expression_terminated.find(container_info)[0].value
                    state_waiting = jsonpath_expression_waiting.find(container_info)[0].value

                    if state_running != "None":
                        state = "running"
                    if state_terminated != "None":
                        state = "terminated"
                    if state_waiting != "None":
                        state = "waiting"
                    if state_running == "None" and state_waiting == "None" and state_terminated == "None":
                        state = "not_found"
                    return state


# CONTAINER RESTARTS COUNT #
def get_container_restart_count(namespace, pod_name, container_name):
    v1 = client.CoreV1Api()
    pod_list = v1.list_namespaced_pod(namespace)

    for pod in pod_list.items:
        pod_metadata_name = pod.metadata.name

        if pod_metadata_name == pod_name:
            pod_status = str(pod.status).replace("'", '"').replace("\n", "").replace(" ", "")
            pod_status = pod_status.replace("None", '"None"').replace(":True", ':"True"').replace(":False", ':"False"')
            pod_status = re.sub(r'datetime\.datetime\(\d+,\d+,\d+,\d+,\d+,\d+,tzinfo\=tzutc\(\)\)', '"None"', pod_status)
            pod_status = json.loads(pod_status)

            jsonpath_expression = parse('$.[container_statuses]')
            pod_container_statuses = jsonpath_expression.find(pod_status)[0].value

            for container_info in pod_container_statuses:
                jsonpath_expression = parse('$.name')
                pod_container_statuses_name = jsonpath_expression.find(container_info)[0].value

                if pod_container_statuses_name == container_name:
                    jsonpath_expression_restart_count = parse('$.restart_count')
                    restart_count = jsonpath_expression_restart_count.find(container_info)[0].value

                    return restart_count


# CONTAINER LAST_STATE TERMINATED #
def get_container_last_state_terminated(namespace, pod_name, container_name):
    v1 = client.CoreV1Api()
    pod_list = v1.list_namespaced_pod(namespace)

    for pod in pod_list.items:
        pod_metadata_name = pod.metadata.name

        if pod_metadata_name == pod_name:
            pod_status = str(pod.status).replace("'", '"').replace("\n", "").replace(" ", "")
            pod_status = pod_status.replace("None", '"None"').replace(":True", ':"True"').replace(":False", ':"False"')
            pod_status = re.sub(r'datetime\.datetime\(\d+,\d+,\d+,\d+,\d+,\d+,tzinfo\=tzutc\(\)\)', '"None"', pod_status)
            pod_status = json.loads(pod_status)

            jsonpath_expression = parse('$.[container_statuses]')
            pod_container_statuses = jsonpath_expression.find(pod_status)[0].value

            for container_info in pod_container_statuses:
                jsonpath_expression = parse('$.name')
                pod_container_statuses_name = jsonpath_expression.find(container_info)[0].value

                if pod_container_statuses_name == container_name:
                    jsonpath_expression_last_state_terminated = parse('$.last_state.terminated')
                    last_state_terminated = jsonpath_expression_last_state_terminated.find(container_info)[0].value
                    if last_state_terminated == "None":
                        return last_state_terminated
                    else:
                        jsonpath_expression_reason = parse('$.reason')
                        jsonpath_expression_exit_code = parse('$.exit_code')
                        reason = jsonpath_expression_reason.find(last_state_terminated)[0].value
                        exit_code = jsonpath_expression_exit_code.find(last_state_terminated)[0].value
                        describe_terminated = f"{reason}: {exit_code}"
                        return describe_terminated


# ACTION FOR ZABBIX ITEM #
if input_action == "GET_LLD_ITEMS":
    get_ns_pods_containers()


if input_action == "GET_CONTAINER_METRICS":
    input_item = input_item.replace("NS:", "").replace("POD:", "").replace("CONTAINER:", "")
    input_item = input_item.split("/")
    namespace = input_item[0]
    pod_name = input_item[1]
    container_name = input_item[2]

    get_container_metrics(namespace, pod_name, container_name)
