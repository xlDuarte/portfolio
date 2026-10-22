"""Kafka producer + bounded consumer for synthetic demo events.

Uses real KafkaProducer/KafkaConsumer when a broker is available.
Default bootstrap localhost:19092 (Redpanda docker compose external listener).
No fake success when Kafka is offline; errors propagate to the caller.
"""
from __future__ import annotations
import argparse
import json
from .engine import generate,connect,ingest,read_events

TOPIC="synthetic-industrial-events-v1"

def publish(project:int,count:int=96,bootstrap:str="localhost:19092",topic:str=TOPIC)->dict:
    from kafka import KafkaProducer
    rows=generate(project,count=count)
    producer=KafkaProducer(bootstrap_servers=bootstrap,acks="all",retries=2,
                           key_serializer=lambda k:k.encode("utf-8"),
                           value_serializer=lambda v:json.dumps(v,sort_keys=True).encode("utf-8"),
                           request_timeout_ms=10000,max_block_ms=10000)
    try:
        for row in rows:
            future=producer.send(topic,key=str(project),value=row)
            # Waiting on broker ACK guarantees this is a real send, not a mock.
            future.get(timeout=12)
        producer.flush(timeout=12)
    finally:producer.close()
    return {"published":len(rows),"topic":topic,"transport":"real Kafka with broker ACK"}

def consume(db_path:str,bootstrap:str="localhost:19092",topic:str=TOPIC,
            max_messages:int=96,group_id:str="synthetic-advanced-lab")->dict:
    from kafka import KafkaConsumer
    if not isinstance(max_messages,int) or not 1<=max_messages<=2000:
        raise ValueError("max_messages 1..2000")
    consumer=KafkaConsumer(topic,bootstrap_servers=bootstrap,group_id=group_id,
        enable_auto_commit=False,auto_offset_reset="earliest",
        value_deserializer=lambda b:json.loads(b.decode("utf-8")),
        consumer_timeout_ms=5000,max_poll_records=200)
    processed=0
    inserted=0
    try:
        with connect(db_path) as db:
            for message in consumer:
                summary=ingest(db,[message.value])
                inserted+=summary["inserted"]
                processed+=1
                # Offset commit after durable SQLite write.
                consumer.commit()
                if processed>=max_messages:break
    finally:consumer.close()
    return {"messages_consumed":processed,"inserted":inserted,
            "duplicates":processed-inserted,"db_path":db_path}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("action",choices=["publish","consume"])
    p.add_argument("--project",type=int,default=91)
    p.add_argument("--count",type=int,default=96)
    p.add_argument("--db",default="/tmp/advanced-kafka-demo.sqlite3")
    p.add_argument("--bootstrap",default="localhost:19092")
    p.add_argument("--topic",default=TOPIC)
    a=p.parse_args()
    out=(publish(a.project,a.count,a.bootstrap,a.topic) if a.action=="publish"
         else consume(a.db,a.bootstrap,a.topic,a.count))
    print(json.dumps(out,indent=2))
if __name__=="__main__":
    main()
