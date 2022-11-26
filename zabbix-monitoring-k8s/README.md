# Zabbix monitoring k8s
This script is designed to integrate and configure monitoring of k8s infrastructure and services using zabbix

## Requirements
- [kubernetes 25.3.0](https://pypi.org/project/kubernetes/)

## Example
```sh
# Autodescaver all containers in k8s cluster
python3 zabbix-monitoring-k8s.py --action "GET_LLD_ITEMS"
# Getting metrics about the specified container
python3 zabbix-monitoring-k8s.py --action "GET_CONTAINER_METRICS" --item "NS:namespace-1/POD:pod-0/CONTAINER:container-0"
```