
import base64
import boto3
import botocore.config
import botocore.exceptions
import click
import gzip
from io import BytesIO
import json
import time
import os


from cdk import (
    INDEXER_FUNCTION_NAME_EXPORT_NAME,
    SEARCHER_FUNCTION_NAME_EXPORT_NAME,
    INDEX_STORE_BUCKET_NAME_EXPORT_NAME,
    QUICKWIT_LAMBDA_STACK_NAME,
)

region = os.environ["CDK_REGION"]

INDEXING_BOTO_CONFIG = botocore.config.Config(
    retries={"max_attempts": 0}, read_timeout=60 * 15
)
session = boto3.Session(region_name=region)
client = session.client("cloudformation")
stacks = client.describe_stacks(StackName=QUICKWIT_LAMBDA_STACK_NAME)["Stacks"]

def get_cloudformation_output_value(export_name: str) -> str:
    if len(stacks) != 1:
        print(f"Quickiwt stack not identified uniquely, found {stacks}")
    outputs = stacks[0]["Outputs"]
    for output in outputs:
        if output["ExportName"] == export_name:
            return output["OutputValue"]
    else:
        print(f"Export name {export_name} not found in Quickwit stack")
        exit(1)

@click.group()
def cli():
    pass

@click.command()
@click.argument('input-s3-path')
def index(input_s3_path):
    function_name = get_cloudformation_output_value(INDEXER_FUNCTION_NAME_EXPORT_NAME)
    print(f"indexer function name: {function_name}")
    if not input_s3_path.startswith("s3://"):
        bucket_name = get_cloudformation_output_value(INDEX_STORE_BUCKET_NAME_EXPORT_NAME)
        input_s3_path = f"s3://{bucket_name}/{input_s3_path}"
    print(f"src_file: {input_s3_path}")
    invoke_start = time.time()
    resp = session.client("lambda", config=INDEXING_BOTO_CONFIG).invoke(
        FunctionName=function_name,
        InvocationType="RequestResponse",
        LogType="Tail",
        Payload=f"""{{ "source_uri": "{input_s3_path}" }}""",
    )
    invoke_duration = time.time() - invoke_start
    print(f"invoke duration: {invoke_duration}")
    print(resp["Payload"].read().decode("utf-8"))

@click.command()
@click.argument('json_query')
def search(json_query):
    function_name = get_cloudformation_output_value(SEARCHER_FUNCTION_NAME_EXPORT_NAME)
    print(f"searcher function name: {function_name}")
    lambda_client = session.client("lambda")
    invoke_start = time.time()
    resp = lambda_client.invoke(
        FunctionName=function_name,
        InvocationType="RequestResponse",
        LogType="Tail",
        Payload=json.dumps(
            {
                "headers": {"Content-Type": "application/json"},
                "requestContext": {
                    "http": {"method": "POST"},
                },
                "body": json_query,
                "isBase64Encoded": False,
            }
        ),
    )
    invoke_duration = time.time() - invoke_start
    print(f"invoke duration: {invoke_duration}")
    print(decode_payload(resp["Payload"]))

def decode_payload(payload):
    gw_str = payload.read().decode()
    gw_obj = json.loads(gw_str)
    payload = gw_obj["body"]
    if gw_obj["isBase64Encoded"]:
        dec_payload = base64.b64decode(payload)
        if gw_obj.get("headers", {}).get("content-encoding", "") == "gzip":
            payload = (
                gzip.GzipFile(mode="rb", fileobj=BytesIO(dec_payload))
                    .read()
                    .decode()
            )
        else:
            payload = dec_payload.decode()
    return payload

cli.add_command(index)
cli.add_command(search)

if __name__ == '__main__':
    cli()
