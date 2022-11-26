#!/usr/bin/env python3
import requests
import json
import argparse
import os
import logging
import re
import random
import string
from datetime import datetime, timedelta
from jsonpath_ng import jsonpath, parse
from elasticsearch import Elasticsearch



##################### INPUT ARGS #####################
parser = argparse.ArgumentParser()
parser.add_argument('--action', type=str, default='null')
parser.add_argument('--item', type=str, default='null')
args = parser.parse_args()
input_action = args.action
input_item = args.item

##################### SET ES VALUES #####################
#logging.basicConfig(level=logging.DEBUG)
endpoint_es_prod = 'http://elastic:9220/'
user_es_prod = 'user'
pass_es_prod = '***'
user_es_prod_write = 'user'
pass_es_prod_write = '***'
endpoint_es_qa = 'https://elastic-dev:9200/'
user_es_qa = 'user'
pass_es_qa = '***'
now = datetime.utcnow()
current_date = now.strftime('%Y.%m.%d')
es_index_monitoring = "es-monitoring-indeces-stat"


##################### EXLUDE RULE VALUE #####################
exclude_aliases_prod = ['index1', 'index2', 'index3']
exclude_indices_prod = ['es-monitoring-indeces-stat']
exclude_indices_qa = ['index1', 'index2', 'index3-{}'.format(current_date)]

##################### CACHE FILES #####################
cache_aliases_prod = '/usr/lib/zabbix/externalscripts/es_monitoring_api_cache/cache_aliases_prod.json'
cache_indices_prod = '/usr/lib/zabbix/externalscripts/es_monitoring_api_cache/cache_indices_prod.json'
cache_nodes_prod = '/usr/lib/zabbix/externalscripts/es_monitoring_api_cache/cache_nodes_prod.json'
cache_indices_qa = '/usr/lib/zabbix/externalscripts/es_monitoring_api_cache/cache_indices_qa.json'
if not os.path.exists('/usr/lib/zabbix/externalscripts/es_monitoring_api_cache'):
    os.makedirs('/usr/lib/zabbix/externalscripts/es_monitoring_api_cache')


##################### MAIN DEFS #####################
### GET REQUESTS TO ES - PROD/QA ###
def request_to_es(URL,USER,PASS,JSON):
    response = requests.get(URL,
        auth = (USER, PASS),
        headers = {'Content-Type': 'application/json'},
        json = JSON
    )
    return response.content


### GET ALIASES CACHE DUMP - PROD ###
def get_cache_aliases_prod():
    URL = endpoint_es_prod+"_cat/aliases?format=json"
    HTTP_METHOD = 'get'
    USER = user_es_prod
    PASS = pass_es_prod
    JSON = {}
    json_aliases = []
 
    response = json.loads(request_to_es(URL,USER,PASS,JSON))

    for item in response:
        item_alias = {"{#ALIAS}": item["alias"]}
        if (item_alias not in json_aliases and item["alias"] not in exclude_aliases_prod and bool(re.match(r'\.', item["alias"])) == False):
            json_aliases.append(item_alias)
    lld_json_aliases = json.dumps({"data":json_aliases})
    with open(cache_aliases_prod, 'w') as outfile:
        json.dump(lld_json_aliases, outfile)
    return "aliases cache for PROD has been updated"


### GET INDECES CACHE DUMP - QA ###
def get_cache_indices_qa():
    URL = endpoint_es_qa+"_cat/indices?format=json"
    HTTP_METHOD = 'get'
    USER = user_es_qa
    PASS = pass_es_qa
    json_indices = []
    JSON = {}
    
    response = json.loads(request_to_es(URL,USER,PASS,JSON))  
    for item in response:
        if current_date in item["index"]:
            item_index = {"{#INDICES}": item["index"]}
            if (item_index not in json_indices and item["index"] not in exclude_indices_qa):
                json_indices.append(item_index)
    lld_json_indices = json.dumps({"data":json_indices})
    with open(cache_indices_qa, 'w') as outfile:
        json.dump(lld_json_indices, outfile) 
    return "indices cache for QA has been updated"


### GET INDECES CACHE DUMP - PROD ###
def get_cache_indices_prod():  
    URL = endpoint_es_prod+"_cat/indices?format=json&h=index"
    HTTP_METHOD = 'get'
    USER = user_es_prod
    PASS = pass_es_prod
    JSON = {}
    json_indices = []

    response = json.loads(request_to_es(URL,USER,PASS,JSON))
    for item in response:
        item_index = {"{#INDEX}": item["index"]}
        if (item_index not in json_indices and item["index"] not in exclude_indices_prod and bool(re.match(r'\.', item["index"])) == False):
            json_indices.append(item_index)
    lld_json_indices = json.dumps({"data":json_indices})
    with open(cache_indices_prod, 'w') as outfile:
        json.dump(lld_json_indices, outfile) 
    return "indices cache for PROD has been updated" 


### GET INDICES SIZE ###
def get_index_size_prod(index_fullname):
    URL = endpoint_es_prod+index_fullname+"/_stats?format=json"
    HTTP_METHOD = 'get'
    USER = user_es_prod
    PASS = pass_es_prod
    JSON = {}
    response = json.loads(request_to_es(URL,USER,PASS,JSON))
    jsonpath_expression = parse('$._all.primaries.store.size_in_bytes')
    match = jsonpath_expression.find(response)
    return match[0].value


### GET INDICES SIZE ###
def get_index_docs_coun_prod(index_fullname):
    URL = endpoint_es_prod+index_fullname+"/_stats?format=json"
    HTTP_METHOD = 'get'
    USER = user_es_prod
    PASS = pass_es_prod
    JSON = {}
    response = json.loads(request_to_es(URL,USER,PASS,JSON))
    jsonpath_expression = parse('$._all.primaries.docs.count')
    match = jsonpath_expression.find(response)
    return match[0].value


### CREATE INDEX IN ELASTICSEARCH FOR INDICES METRICS ###
def create_index_in_elasticsearch(index_name):
    es_object = Elasticsearch([endpoint_es_prod], http_auth=[user_es_prod_write, pass_es_prod_write])
    index_settings = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 1
            },
            "mappings": {
                    "dynamic": "strict",
                    "properties": {
                        "@timestamp": {
                            "type": "date",
                            "format": "yyyy.MM.dd"
                        },                    
                        "index_name": {
                            "type": "text",
                            "fields": {
                            "keyword": {
                                "ignore_above": 256,
                                "type": "keyword"
                            }
                            }                            
                        },
                        "size_in_bytes": {
                            "type": "long"
                        },
                        "docs_count": {
                            "type": "long"
                        },                    
                    }
            }
        }
    es_object.indices.create(index = index_name, body = index_settings, ignore=[400])
    return es_object


### WRITE DATA TO ELASTICSEARCH INDEX ###
def es_post_document(es_object,index,body):
    doc_id = get_random_string(24)
    response = es_object.index(index=index, id=doc_id, body=body,request_timeout=60)
    return response['result']


### GET RANDOM STRING ###
def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_letters) for i in range(length))
    return result_str


##################### IF INPUT ACTIONS - INDECES/ALIASES CHECKS #####################

### GET ALIASES LIST TO ZABBIX LLD FOR THE CACHE-FILE - PROD ###
if input_action == "get_aliases_prod":
    result = get_cache_aliases_prod()
    with open(cache_aliases_prod) as json_file:
        data = json.load(json_file)
    print(data)


### GET INDECES LIST TO ZABBIX LLD FOR THE CACHE-FILE - QA ###
if input_action == "get_indices_qa":
    result = get_cache_indices_qa()
    with open(cache_indices_qa) as json_file:
        data = json.load(json_file)
    print(data)


### GET INDICES LIST FOR CAHE DUMP - PROD ###
if input_action == "get_indices_prod":
    result = get_cache_indices_prod()
    with open(cache_indices_prod) as json_file:
        data = json.load(json_file)
    print(data)


### CHECK ALIASIS UPDATE LOGS FOR ITEMS ZABBIX - PROD ###
if input_action == "get_status_aliases_prod":
    URL = endpoint_es_prod+input_item+"/_search"
    HTTP_METHOD = 'get'
    USER = user_es_prod
    PASS = pass_es_prod
    JSON = {"version": 'true', 
            "size": 1, 
            "sort": [ 
                { "@timestamp": { 
                    "order": "desc", 
                    "unmapped_type": "boolean" } } ], 
            "query": { 
                "bool": { 
                    "must": [ { 
                        "match_all": {} },
                         { "range": { 
                             "@timestamp": { 
                                 "gte": "now-30m", 
                                 "lte": "now", 
                                 "format": "epoch_millis" } } } ], 
                    "must_not":[]}}}
    response = json.loads(request_to_es(URL,USER,PASS,JSON))

    jsonpath_expression = parse('$.hits.hits[*]._id')
    try:
        match = jsonpath_expression.find(response)[0].value
        print('updated')
    except:
        print('not_updated')


### CHECK INDICES UPDATE LOGS FOR ITEMS ZABBIX - QA ###
if input_action == "get_status_indices_qa":
    URL = endpoint_es_qa+input_item+"/_search"
    HTTP_METHOD = 'get'
    USER = user_es_qa
    PASS = pass_es_qa
    JSON = {"version": 'true', 
            "size": 1, 
            "sort": [ 
                { "@timestamp": { 
                    "order": "desc", 
                    "unmapped_type": "boolean" } } ], 
            "query": { 
                "bool": { 
                    "must": [ { 
                        "match_all": {} },
                         { "range": { 
                             "@timestamp": { 
                                 "gte": "now-1h", 
                                 "lte": "now", 
                                 "format": "epoch_millis" } } } ], 
                    "must_not":[]}}}
    response = json.loads(request_to_es(URL,USER,PASS,JSON))

    jsonpath_expression = parse('$.hits.hits[*]._id')
    try:
        match = jsonpath_expression.find(response)[0].value
        print('updated')
    except:
        print('not_updated')


### GET INDICES WITHOUT ALIAS - PROD ###
if input_action == "check_alias_for_index_prod":
    URL = endpoint_es_prod+input_item+"/_alias?format=json"
    HTTP_METHOD = 'get'
    USER = user_es_prod
    PASS = pass_es_prod
    JSON = {}
    response = json.loads(request_to_es(URL,USER,PASS,JSON))

    jsonpath_expression = parse('$."{}".aliases'.format(input_item))
    try:
        match = jsonpath_expression.find(response)
        string = str(match[0].value)[1:-1]
        if not string:
            print('alias_not_found')
        else:
            print('alias_exist')
    except:
        print('alias_not_found')


### GET INDICES WITHOUT ALIAS - PROD ###
if input_action == "check_read_only_index_prod":
    URL = endpoint_es_prod+input_item+"/_settings?format=json"
    HTTP_METHOD = 'get'
    USER = user_es_prod
    PASS = pass_es_prod
    JSON = {}
    response = json.loads(request_to_es(URL,USER,PASS,JSON))

    jsonpath_expression_read_only_allow_delete = parse('$."{}".settings.index.blocks.read_only_allow_delete'.format(input_item))
    jsonpath_expression_read_only = parse('$."{}".settings.index.blocks.read_only'.format(input_item))
    try:
        match_read_only_allow_delete = jsonpath_expression_read_only_allow_delete.find(response)
        if match_read_only_allow_delete[0].value == 'true':
            print('read_only_allow_delete')
        else:
            match2 = jsonpath_expression_read_only.find(response)
            if match2[0].value == 'true':
                print('read_only')
            else:
                print('not_found_key')                
    except:
        try:
            match_read_only = jsonpath_expression_read_only.find(response)
            if match_read_only[0].value == 'true':
                print('read_only')
        except:
            print('not_found_key')


##################### IF INPUT ACTIONS - CLUSTER/NODES CHECKS #####################
### GET NODES STAT - PROD ###
if input_action == "get_nodes_lld_prod":
    URL = endpoint_es_prod+"_cat/nodes?format=json&full_id=true&h=name,id"
    HTTP_METHOD = 'get'
    USER = user_es_prod
    PASS = pass_es_prod
    JSON = {}
    json_nodes = []
    response = json.loads(request_to_es(URL,USER,PASS,JSON))

    with open(cache_nodes_prod, 'w') as outfile:
        json.dump(response, outfile)
    for item in response:
        item = {"{#NODE}": item['name']}
        json_nodes.append(item)
    lld_json_nodes = json.dumps({"data":json_nodes})
    print(lld_json_nodes)


### GET NODES STAT - PROD ###
if input_action == "get_nodes_stat_prod":
    URL = endpoint_es_prod+"_nodes/"+input_item+"/stats"
    HTTP_METHOD = 'get'
    USER = user_es_prod
    PASS = pass_es_prod
    JSON = {}
    response = json.loads(request_to_es(URL,USER,PASS,JSON))
    
    file = open(cache_nodes_prod, 'r')
    data_json = json.load(file)
    for item in data_json:
        if item['name'] == input_item:
            node_id = item['id']
    jsonpath_expression = parse('$.nodes."{}"'.format(str(node_id)))
    match = jsonpath_expression.find(response)
    data_json = json.dumps(match[0].value)
    print(data_json)


### GET CLUSTER STATS PER NODE - PROD ###
if input_action == "get_cluster_stats_node_prod":
    URL = endpoint_es_prod+"_cluster/stats/nodes/"+input_item
    HTTP_METHOD = 'get'
    USER = user_es_prod
    PASS = pass_es_prod
    JSON = {}
    response = json.loads(request_to_es(URL,USER,PASS,JSON))
    data_json = json.dumps(response)
    print(data_json)


### GET CLUSTER STATS - PROD ###
if input_action == "get_cluster_stats_prod":
    URL = endpoint_es_prod+"_cluster/stats"
    HTTP_METHOD = 'get'
    USER = user_es_prod
    PASS = pass_es_prod
    JSON = {}
    response = json.loads(request_to_es(URL,USER,PASS,JSON))
    data_json = json.dumps(response)
    print(data_json)


### GET CLUSTER HEALTH - PROD ###
if input_action == "get_cluster_health_prod":
    URL = endpoint_es_prod+"_cluster/health"
    HTTP_METHOD = 'get'
    USER = user_es_prod
    PASS = pass_es_prod
    JSON = {}
    response = json.loads(request_to_es(URL,USER,PASS,JSON))
    data_json = json.dumps(response)
    print(data_json)


### GET CLUSTER HEALTH - PROD ###
if input_action == "get_cluster_active_master_prod":
    URL = endpoint_es_prod+"_cat/master?format=json&h=node"
    HTTP_METHOD = 'get'
    USER = user_es_prod
    PASS = pass_es_prod
    JSON = {}
    response = json.loads(request_to_es(URL,USER,PASS,JSON))
    data_json = json.dumps(response)
    print(data_json)


##################### IF INPUT ACTIONS - WITHOUT ZABBIX ITEM #####################

### GET INDICES LIST FOR CACHE DUMP BY MASK - PROD (CRONTAB RUN)###
# ex. index-service-*
if input_action == "get_stats_indices_size_prod":
    result = get_cache_indices_prod()
    item_array = []
    es_object = create_index_in_elasticsearch(es_index_monitoring)
    date_for_get_stats = datetime.today() - timedelta(days=1)
    date_for_get_stats = date_for_get_stats.strftime("%Y.%m.%d")
    print("date_for_get_stats: " + str(date_for_get_stats))
    with open(cache_indices_prod) as json_file:
        json_string = json.load(json_file)
        json_object = json.loads(json_string)
    
        for item in json_object['data']:
            item_value = item['{#INDEX}']
            index_date = re.sub(r'\w*-(\w*-)?(\w*-)?(\w*-)?||(_\d*)?','',item_value)
            index_name = re.sub(r'-\d\d\d\d.*','',item_value)
    
            if re.match(r'\d\d\d\d.\d\d.\d\d',index_date):
                try:
                    index_date = datetime.strptime(index_date, "%Y.%m.%d").strftime("%Y.%m.%d")
                except:
                    index_date = index_date.replace("_1","")
                    index_date = datetime.strptime(index_date, "%Y.%m.%d").strftime("%Y.%m.%d")
                    
                if index_date == date_for_get_stats:
                    size_in_bytes = get_index_size_prod(item_value)
                    docs_count = get_index_docs_coun_prod(item_value)
                    json_body = {
                        '@timestamp': index_date,
                        'index_name': index_name,
                        'size_in_bytes': size_in_bytes,
                        'docs_count': docs_count
                    }
                    es_post_document(es_object,es_index_monitoring,json_body)
                    print(json_body)
            else:
                index_date = date_for_get_stats
                index_name = item_value
                size_in_bytes = get_index_size_prod(item_value)
                docs_count = get_index_docs_coun_prod(item_value)
                json_body = {
                    '@timestamp': index_date,
                    'index_name': index_name,
                    'size_in_bytes': size_in_bytes,
                    'docs_count': docs_count
                }
                es_post_document(es_object,es_index_monitoring,json_body)
                print(json_body)


### GET INDICES LIST FOR CAHE DUMP BY MASK - PROD (MANUALLY RUN)###
# ex. index-service-*
if input_action == "get_stats_indices_size_prod_once":
    result = get_cache_indices_prod()
    item_array = []
    es_object = create_index_in_elasticsearch(es_index_monitoring)

    with open(cache_indices_prod) as json_file:
        json_string = json.load(json_file)
        json_object = json.loads(json_string)
    
        for item in json_object['data']:
            item_value = item['{#INDEX}']
            index_date = re.sub(r'\w*-(\w*-)?(\w*-)?(\w*-)?||(_\d*)?','',item_value)
            index_name = re.sub(r'-\d\d\d\d.*','',item_value)
    
            if re.match(r'\d\d\d\d.\d\d.\d\d',index_date):
                index_date = datetime.strptime(index_date, "%Y.%m.%d").strftime("%Y.%m.%d")
    
                if index_date != current_date:
                    size_in_bytes = get_index_size_prod(item_value)
                    docs_count = get_index_docs_coun_prod(item_value)
                    json_body = {
                        '@timestamp': index_date,
                        'index_name': index_name,
                        'size_in_bytes': size_in_bytes,
                        'docs_count': docs_count
                    }
                    es_post_document(es_object,es_index_monitoring,json_body)
                    print(json_body)

            else: 
                print("no_ratation "+index_date)