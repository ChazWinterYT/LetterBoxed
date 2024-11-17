import os
import boto3
import json
import pytest
from moto import mock_aws

# Set up environment variables for the test environment
table_name = os.environ["GAME_TABLE"] = "LetterBoxedGamesTest"
bucket_name = os.environ["S3_BUCKET_NAME"] = "test-dictionary-bucket"
dictionary_path = os.environ["DICTIONARY_BASE_S3_PATH"] = "Dictionaries/"
default_language = os.environ["DEFAULT_LANGUAGE"] = "en"


def test_full_app_integration():
    # Initialize AWS clients
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    s3 = boto3.client("s3", region_name="us-east-1")

    # Ensure test resources are clean before starting
    cleanup_dynamodb_table(dynamodb)
    cleanup_s3_bucket(s3)
    assert_table_empty(dynamodb, table_name)
    assert_bucket_empty(s3, bucket_name)

    # Begin Integration Tests
    

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
