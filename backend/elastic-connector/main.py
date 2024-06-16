from kafka import KafkaConsumer,KafkaProducer
import os
import json
from typing import Dict,List
from elasticsearch import Elasticsearch,helpers
import time
KAFKA_ADDRESS=os.environ['REDPANDA_ADDR']
ELASTIC_PASSWORD=os.environ['ELASTIC_PASSWORD']
ELASTIC_INDEX="raw"
SAMPLE_SIZE=1
consumer=KafkaConsumer('raw-input',bootstrap_servers=KAFKA_ADDRESS,group_id="elastic-connector")
producer=KafkaProducer(bootstrap_servers=KAFKA_ADDRESS,acks="all")
elastic=Elasticsearch(hosts='http://elastic:9200',basic_auth=("elastic",ELASTIC_PASSWORD))
def parse_item(item):
    item=json.loads(item)
    return {"_index":ELASTIC_INDEX,**item}
def handle_batch(items:List[str]):
    parsed_item=[parse_item(i) for i in items]
    while True:
        try:
            helpers.bulk(client=elastic,actions=iter(parsed_item))
            print("handle_batch ok")
            return
        except Exception as e:
            print(e)
            time.sleep(5)
    
def repush_batch(items):
    while True:
        for item in items:
            try:
                print({"topic":'committed-spark-output', "value":item})
                producer.send(**{"topic":'committed-raw-input', "value":item})
                print("repush_batch ok")
                return
            except Exception as e:
                print(e)
                time.sleep(5)
def topics_to_list(batch):
    result=[]
    for _,v in batch.items():
        try:
            result.extend([item.value for item in v])
        except:
            pass
    return result
def polling():
    while True:
        new_batch=consumer.poll(timeout_ms=10000,max_records=SAMPLE_SIZE)
        if new_batch:
            print(new_batch)
            new_batch=topics_to_list(new_batch)
            handle_batch(new_batch)
            repush_batch(new_batch)
if __name__=="__main__":
    polling()