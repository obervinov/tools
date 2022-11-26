# Zabbix monitoring elasticsearch api
This script is designed to integrate elasticsearch cluster monitoring with zabbix

## Requirements
- [elasticsearch 8.5.2](https://pypi.org/project/elasticsearch/)

## Example
```sh
### Indices and aliases monitoring
# Get a list of aliases for a production cluster
python3 zabbix-es-monitoring.py --action "get_aliases_prod"
# Get a list of indexes for a test cluster
python3 zabbix-es-monitoring.py --action "get_indices_qa"
# Get a list of indexes for a production cluster
python3 zabbix-es-monitoring.py --action "get_indices_prod"
# Check that the data is being written to the aliases of the production cluster
python3 zabbix-es-monitoring.py --action "get_status_aliases_prod" --item "alias-1"
# Check that the data is being written to the indices of the test cluster
python3 zabbix-es-monitoring.py --action "get_status_indices_qa" --item "index-1"
# Check that the index has an alias for the production cluster
python3 zabbix-es-monitoring.py --action "check_alias_for_index_prod" --item "index-1"
# Check that the index does not have the readonly status for the production cluster
python3 zabbix-es-monitoring.py --action "check_read_only_index_prod" --item "index-1"
# Get a list of nodes for the production cluster
python3 zabbix-es-monitoring.py --action "get_nodes_lld_prod"
# Get node metrics in a production cluster
python3 zabbix-es-monitoring.py --action "get_nodes_stat_prod" --item "node-1"
# Get cluster metrics about the specified node for the production cluster
python3 zabbix-es-monitoring.py --action "get_cluster_stats_node_prod" --item "node-1"
# Get cluster metrics from a production cluster
python3 zabbix-es-monitoring.py --action "get_cluster_stats_prod"
# Get health metrics from the production cluster
python3 zabbix-es-monitoring.py --action "get_cluster_health_prod"
# Get the name of the active master for the production cluster
python3 zabbix-es-monitoring.py --action "get_cluster_active_master_prod"
# Get a dump with indexes and statistics about them for the production cluster
python3 zabbix-es-monitoring.py --action "get_stats_indices_size_prod"
# Get a dump with indexes and statistics about them for the production cluster (for testing)
python3 zabbix-es-monitoring.py --action "get_stats_indices_size_prod_once"
```