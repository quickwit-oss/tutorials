# Quickwit + Redpanda Tutorial

In this tutorial, we will start a redpanda instance and 3 quickwit instances, with 3 indexers. The goal of the tutorial is
to see Quickwit consuming data from multiples partitions on a given topic.

## Setup

We need docker compose to start redpanda and quickwit instances. We will then create a topic and push data into with a python script.

### Installing Pipenv

```bash
pip install --user pipenv
```

[Pipenv installation](https://pipenv.pypa.io/en/latest/installation/)

### Installing the dependencies in a virtual environment

We just need the `python-kafka` client.

```bash
pipenv shell
pipenv install
```

## Indexing with Redpanda

### Start Redpanda and Quickwit instances

```bash
docker compose up -d
```

You can go to the redpanda console at [localhost:8080](localhost:8080) and to the Quickwit UI [localhost:7280](localhost:7280).


### Create the index and the kafka source in Quickwit

```bash
# Create the index
curl -XPOST http://localhost:7280/api/v1/indexes -H "content-type: application/yaml" --data-binary @index-config.yaml 
```

### Create a topic in Redpanda with 48 partitions

```
docker compose exec redpanda rpk topic create hdfs-logs -p 48
```

### Create the Redpanda source

```bash
curl -XPOST http://localhost:7280/api/v1/indexes/hdfs-logs/sources -H "content-type: application/yaml" --data-binary @redpanda-source.yaml
```

Quickwit will then create `desired_num_pipelines` (here 48) indexing pipelines as requested as long as there is more partitions than the number of pipelines.

### Send data into Redpanda

Download the HDFS logs dataset and execute the python script which will send the logs into the Redpanda topic.
```bash
wget https://quickwit-datasets-public.s3.amazonaws.com/hdfs-logs-multitenants-10000.json
python send_messages_to_topic.py
```

Checkout [Quickwit UI](http://localhost:7280/ui/search?query=*&index_id=hdfs-logs&max_hits=10&sort_by_field=%2Btimestamp) for logs!


## Cleanup

```bash
docker compose stop
docker compose rm
```

