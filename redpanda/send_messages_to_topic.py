import json
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers = "localhost:19092",
)

topic = "hdfs-logs"

def on_success(metadata):
  print(f"Message produced to topic '{metadata.topic}' at offset {metadata.offset}")

def on_error(e):
  print(f"Error sending message: {e}")


with open("hdfs-logs-multitenants-10000.json", "r") as f:
    for line in f:
        future = producer.send(topic, line.encode("utf-8"))
        future.add_callback(on_success)
        future.add_errback(on_error)

    producer.flush()
    producer.close()
