# Quickwit AWS Lambda Tutorial

## Installing Pipenv

```bash
pip install --user pipenv
```

[Pipenv installation](https://pipenv.pypa.io/en/latest/installation/)

## Installing the dependencies in a virtual environment

```bash
pipenv shell
pipenv install
```

## Download Quickwit Lambdas

```bash
mkdir -p cdk.out
wget -P cdk.out https://github.com/quickwit-oss/quickwit/releases/download/aws-lambda-beta/quickwit-lambda-indexer-beta-01-x86_64.zip
wget -P cdk.out  https://github.com/quickwit-oss/quickwit/releases/download/aws-lambda-beta/quickwit-lambda-searcher-beta-01-x86_64.zip
```

## Boostrap CDK


```bash
export CDK_ACCOUNT=XXXXXX
export CDK_REGION=us-east-1
cdk bootstrap aws://$CDK_ACCOUNT/$CDK_REGION
```

## Setup your index config

In this tutorial, we will index logs from the HDFS logs datasets (link) and the provided config index-config.yaml.

## Deploy Quickwit Lambda Stack

First delete all objects in the S3 buckets created for this stack.

Then run:

```bash
cdk deploy -a app.py QuickwitLambdaStack
```

## Index data

```bash
python cli.py index s3://quickwit-datasets-public/hdfs-logs-multitenants-10000.json
```

## Search data

```bash
python cli.py search '{"query":"severity_text:ERROR"}'
```

## Cleanup

```bash
cdk destroy -a cdk/app.py
rm -rf cdk.out
```
