# Using 3008MB as default because higher memory configurations need to be
# enabled for each AWS account through the support.
QUICKWIT_LAMBDA_STACK_NAME = "QuickwitLambdaStack"
DEFAULT_LAMBDA_MEMORY_SIZE = 3008
INDEX_STORE_BUCKET_NAME_EXPORT_NAME = "quickwit-index-store-bucket-name"
INDEXER_FUNCTION_NAME_EXPORT_NAME = "quickwit-indexer-function-name"
SEARCHER_FUNCTION_NAME_EXPORT_NAME = "quickwit-searcher-function-name"
INDEXER_PACKAGE_LOCATION = "cdk.out/quickwit-lambda-indexer-beta-01-x86_64.zip"
SEARCHER_PACKAGE_LOCATION = "cdk.out/quickwit-lambda-searcher-beta-01-x86_64.zip"
RUST_LOG = "quickwit=info"
