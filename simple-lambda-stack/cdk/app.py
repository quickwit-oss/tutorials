#!/usr/bin/env python3

import os
import yaml
import aws_cdk
from aws_cdk import Stack, aws_s3_assets, aws_s3, aws_lambda, aws_iam
from constructs import Construct

from constants import (
    QUICKWIT_LAMBDA_STACK_NAME,
    DEFAULT_LAMBDA_MEMORY_SIZE,
    INDEX_STORE_BUCKET_NAME_EXPORT_NAME,
    INDEXER_FUNCTION_NAME_EXPORT_NAME,
    SEARCHER_FUNCTION_NAME_EXPORT_NAME,
    INDEXER_PACKAGE_LOCATION,
    SEARCHER_PACKAGE_LOCATION,
    RUST_LOG,
)

def extract_local_env() -> dict[str, str]:
    """Extracts local environment variables that start with QW_LAMBDA_"""
    return {k: os.environ[k] for k in os.environ.keys() if k.startswith("QW_LAMBDA_")}

class QuickwitLambdaStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        indexer_memory_size: int,
        searcher_memory_size: int,
        indexer_package_location: str,
        searcher_package_location: str,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        index_config_path = os.getenv("INDEX_CONFIG_PATH", "index-config.yaml")
        with open(index_config_path) as f:
            index_config_dict = yaml.safe_load(f)
            index_id = index_config_dict["index_id"]
        index_config = aws_s3_assets.Asset(
            self,
            "index-config",
            path=index_config_path,
        )
        lambda_env = {
            **extract_local_env(),
            "RUST_LOG": RUST_LOG,
        }
        qw_svc = QuickwitService(
            self,
            "Quickwit",
            index_id=index_id,
            index_config_bucket=index_config.s3_bucket_name,
            index_config_key=index_config.s3_object_key,
            indexer_environment=lambda_env,
            searcher_environment=lambda_env,
            indexer_memory_size=indexer_memory_size,
            searcher_memory_size=searcher_memory_size,
            indexer_package_location=indexer_package_location,
            searcher_package_location=searcher_package_location,
        )
        aws_cdk.CfnOutput(
            self,
            "index-store-bucket-name",
            value=qw_svc.bucket.bucket_name,
            export_name=INDEX_STORE_BUCKET_NAME_EXPORT_NAME,
        )
        aws_cdk.CfnOutput(
            self,
            "indexer-function-name",
            value=qw_svc.indexer.lambda_function.function_name,
            export_name=INDEXER_FUNCTION_NAME_EXPORT_NAME,
        )
        aws_cdk.CfnOutput(
            self,
            "searcher-function-name",
            value=qw_svc.searcher.lambda_function.function_name,
            export_name=SEARCHER_FUNCTION_NAME_EXPORT_NAME,
        )

class QuickwitService(Construct):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        index_config_bucket: str,
        index_config_key: str,
        index_id: str,
        searcher_package_location: str,
        indexer_package_location: str,
        indexer_memory_size: int = 8000,
        indexer_environment: dict[str, str] = {},
        searcher_memory_size: int = DEFAULT_LAMBDA_MEMORY_SIZE,
        searcher_environment: dict[str, str] = {},
        **kwargs,
    ) -> None:
        """Create a new Quickwit Lambda service construct node.

        `{indexer|searcher}_package_location` is the path of the `zip` asset for
        the Lambda function.
        """
        super().__init__(scope, construct_id, **kwargs)
        self.bucket = aws_s3.Bucket(
            self,
            "IndexStore",
            removal_policy=aws_cdk.RemovalPolicy.DESTROY,
        )
        self.indexer = IndexerService(
            self,
            "Indexer",
            store_bucket=self.bucket,
            index_id=index_id,
            index_config_bucket=index_config_bucket,
            index_config_key=index_config_key,
            memory_size=indexer_memory_size,
            environment=indexer_environment,
            asset_path=indexer_package_location,
        )
        self.searcher = SearcherService(
            self,
            "Searcher",
            store_bucket=self.bucket,
            index_id=index_id,
            memory_size=searcher_memory_size,
            environment=searcher_environment,
            asset_path=searcher_package_location,
        )

class IndexerService(Construct):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        store_bucket: aws_s3.Bucket,
        index_id: str,
        index_config_bucket: str,
        index_config_key: str,
        memory_size: int,
        environment: dict[str, str],
        asset_path: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.lambda_function = aws_lambda.Function(
            self,
            id="Lambda",
            code=aws_lambda.Code.from_asset(asset_path),
            runtime=aws_lambda.Runtime.PROVIDED_AL2,
            handler="N/A",
            environment={
                "QW_LAMBDA_INDEX_BUCKET": store_bucket.bucket_name,
                "QW_LAMBDA_METASTORE_BUCKET": store_bucket.bucket_name,
                "QW_LAMBDA_INDEX_ID": index_id,
                "QW_LAMBDA_INDEX_CONFIG_URI": f"s3://{index_config_bucket}/{index_config_key}",
                **environment,
            },
            timeout=aws_cdk.Duration.minutes(15),
            reserved_concurrent_executions=1,
            memory_size=memory_size,
            ephemeral_storage_size=aws_cdk.Size.gibibytes(10),
        )
        self.lambda_function.add_to_role_policy(
            aws_iam.PolicyStatement(
                actions=["s3:GetObject"],
                resources=[f"arn:aws:s3:::{index_config_bucket}/{index_config_key}"],
            )
        )
        store_bucket.grant_read_write(self.lambda_function)

class SearcherService(Construct):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        store_bucket: aws_s3.Bucket,
        index_id: str,
        memory_size: int,
        environment: dict[str, str],
        asset_path: str,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.lambda_function = aws_lambda.Function(
            self,
            id="Lambda",
            code=aws_lambda.Code.from_asset(asset_path),
            runtime=aws_lambda.Runtime.PROVIDED_AL2,
            handler="N/A",
            environment={
                "QW_LAMBDA_INDEX_BUCKET": store_bucket.bucket_name,
                "QW_LAMBDA_METASTORE_BUCKET": store_bucket.bucket_name,
                "QW_LAMBDA_INDEX_ID": index_id,
                **environment,
            },
            timeout=aws_cdk.Duration.seconds(30),
            memory_size=memory_size,
            ephemeral_storage_size=aws_cdk.Size.gibibytes(10),
        )

        store_bucket.grant_read_write(self.lambda_function)

app = aws_cdk.App()

QuickwitLambdaStack(
    app,
    QUICKWIT_LAMBDA_STACK_NAME,
    env=aws_cdk.Environment(
        account=os.getenv("CDK_ACCOUNT"), region=os.getenv("CDK_REGION")
    ),
    indexer_memory_size=int(
        os.environ.get("INDEXER_MEMORY_SIZE", DEFAULT_LAMBDA_MEMORY_SIZE)
    ),
    searcher_memory_size=int(
        os.environ.get("SEARCHER_MEMORY_SIZE", DEFAULT_LAMBDA_MEMORY_SIZE)
    ),
    indexer_package_location=INDEXER_PACKAGE_LOCATION,
    searcher_package_location=SEARCHER_PACKAGE_LOCATION,
)

app.synth()
