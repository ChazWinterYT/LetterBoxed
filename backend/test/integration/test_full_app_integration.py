import os
import boto3
import json
import pytest
import constants
from moto import mock_aws

# Set up environment variables for the test environment
table_name = os.environ["GAME_TABLE"] = "LetterBoxedGamesTest"
bucket_name = os.environ["S3_BUCKET_NAME"] = "test-dictionary-bucket"
dictionary_path = os.environ["DICTIONARY_BASE_S3_PATH"] = "Dictionaries/"
default_language = os.environ["DEFAULT_LANGUAGE"] = "en"


@pytest.fixture(scope="module")
def aws_clients():
    """
    Fixture to initialize AWS clients.
    """
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    s3 = boto3.client("s3", region_name="us-east-1")
    lambda_client = boto3.client("lambda", region_name="us-east-1")
    return {"dynamodb": dynamodb, "s3": s3, "lambda_client": lambda_client}




def test_full_app_integration(aws_clients):
    dynamodb = aws_clients["dynamodb"]
    s3 = aws_clients["s3"]
    lambda_client = aws_clients["lambda_client"]

    # Ensure test resources are clean before starting
    cleanup_dynamodb_table(dynamodb)
    cleanup_s3_bucket(s3)
    assert_table_empty(dynamodb, table_name)
    assert_bucket_empty(s3, bucket_name)

    # ===========================================================================
    # Begin Integration Tests
    # ===========================================================================

    # Setup S3 Dictionary
    add_en_dictionary_to_s3(s3)
    assert_bucket_contains(s3, constants.VALID_DICTIONARY_KEY)

    # Create a custom game
    response = lambda_client.invoke(
        FunctionName="CreateCustomLambda",
        Payload=json.dumps(constants.CREATE_CUSTOM_GAME_PAYLOAD)
    )
    # response_payload = json.loads(response["Payload"].read())
    # assert "statusCode" in response_payload, f"Unexpected response: {response_payload}"
    # assert response_payload["statusCode"] == 200
    # game_id = json.loads(response_payload["body"])["gameId"]
    # assert_dynamodb_item_exists(dynamodb, game_id)

    # Cleanup after tests and verify that resources are clear
    cleanup_dynamodb_table(dynamodb)
    cleanup_s3_bucket(s3)
    assert_table_empty(dynamodb, table_name)
    assert_bucket_empty(s3, bucket_name)


# Cleanup resources and verify cleanup complete
def cleanup_dynamodb_table(dynamodb):
    try:
        table = dynamodb.Table(table_name)
        response = table.scan()
        with table.batch_writer() as batch:
            for item in response.get("Items", []):
                batch.delete_item(Key={"gameId": item["gameId"]})
    except dynamodb.meta.client.exceptions.ResourceNotFoundException:
        print(f"Table {os.environ['GAME_TABLE']} does not exist. Skipping cleanup.")


def add_en_dictionary_to_s3(s3):
    print("Uploading dictionary to S3...")
    s3.put_object(
        Bucket=bucket_name,
        Key=constants.VALID_DICTIONARY_KEY,
        Body=constants.EN_DICTIONARY_1
    )

def assert_bucket_contains(s3, key):
    """Assert that a specific key exists in the S3 bucket."""
    objects = s3.list_objects(Bucket=bucket_name).get("Contents", [])
    keys = [obj["Key"] for obj in objects]
    assert key in keys, f"Key {key} not found in bucket {bucket_name}."

def assert_dynamodb_item_exists(dynamodb, game_id):
    """Assert that a specific item exists in DynamoDB."""
    table = dynamodb.Table(table_name)
    response = table.get_item(Key={"gameId": game_id})
    assert "Item" in response, f"Item with gameId {game_id} not found in DynamoDB."

# ===========================================================================
# Cleanup Utilities
# ===========================================================================
def cleanup_s3_bucket(s3):
    try:
        response = s3.list_objects(Bucket=bucket_name)
        if "Contents" in response:
            for obj in response["Contents"]:
                s3.delete_object(Bucket=bucket_name, Key=obj["Key"])
    except s3.exceptions.NoSuchBucket:
        print(f"Bucket {bucket_name} does not exist. Skipping cleanup.")

def assert_bucket_empty(s3, bucket_name):
    objects = s3.list_objects(Bucket=bucket_name).get("Contents", [])
    assert len(objects) == 0, f"Bucket {bucket_name} is not empty. Found objects: {objects}"

def assert_table_empty(dynamodb, table_name):
    table = dynamodb.Table(table_name)
    scan = table.scan()
    assert scan["Count"] == 0, f"Table {table_name} is not empty. Found items: {scan['Items']}"
