#!/usr/bin/env python
import argparse
import boto3
import datetime
import logging
import json
from kafka import KafkaProducer

logging.basicConfig(level=logging.DEBUG)


parser = argparse.ArgumentParser()
parser.add_argument('--days', type=int, default=30)
args = parser.parse_args()

now = datetime.datetime.utcnow()
start = (now - datetime.timedelta(days=args.days)).strftime('%Y-%m-%d')
end = now.strftime('%Y-%m-%d')

cd = boto3.client('ce', 'us-east-1')

results = []

token = None


def publish_message_kafka(producer_instance, topic_name, key, value):
    try:
        key_bytes = bytes(key, encoding='utf-8')
        value_bytes = bytes(value, encoding='utf-8')
        producer_instance.send(topic_name, key=key_bytes, value=value_bytes)
        producer_instance.flush()
        print('Message published successfully.')
    except Exception as ex:
        print('Exception in publishing message')
        print(str(ex))


def connect_kafka_producer():
    _producer = None
    try:
        _producer = KafkaProducer(
                        bootstrap_servers=['kafka-1.example.com:9093'],
                        api_version=(0, 10),
                        security_protocol='SSL',
                        ssl_check_hostname=True,
                        ssl_cafile='kafka_client.truststore.pem',
                        ssl_certfile='kafka_client.keystore.pem',
                        ssl_keyfile='kafka_client.keystore.key'
                    )
    except Exception as ex:
        print('Exception while connecting Kafka')
        print(str(ex))
    finally:
        return _producer


def send_kafka(key_value):
    kafka_producer = connect_kafka_producer()
    topic = "topic"
    key = "message"
    publish_message_kafka(kafka_producer, topic, key, key_value)
    if kafka_producer is not None:
        kafka_producer.close()
        return "send_kafka successfully"


while True:
    if token:
        kwargs = {'NextPageToken': token}
    else:
        kwargs = {}
    data = cd.get_cost_and_usage(
                TimePeriod={'Start': start, 'End':  end},
                Granularity='DAILY',
                Metrics=['UnblendedCost'],
                GroupBy=[
                    {'Type': 'DIMENSION', 'Key': 'LINKED_ACCOUNT'},
                    {'Type': 'DIMENSION', 'Key': 'SERVICE'}
                ],
                **kwargs
            )
    results += data['ResultsByTime']
    token = data.get('NextPageToken')
    if not token:
        break

for result_by_time in results:
    for group in result_by_time['Groups']:
        amount = group['Metrics']['UnblendedCost']['Amount']
        timestamp = result_by_time['TimePeriod']['Start']
        keys = group['Keys'][0]
        service_name = group['Keys'][1]
        json_data = {
            '@timestamp': timestamp,
            'keys': keys,
            'service_name': service_name,
            'amount': amount,
            'tags': 'aws-coast'
        }
        json_out = json.dumps(json_data)
        try:
            send_kafka(json_out)
        except Exception as err:
            print(str(err))
