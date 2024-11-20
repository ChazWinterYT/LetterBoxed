import os
import boto3
import json
import pytest
import constants

# Set up environment variables for the test environment
games_table_name = os.environ["GAMES_TABLE_NAME"] = "LetterBoxedGamesTest"
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

@pytest.fixture(scope="module")
def setup_aws_resources(aws_clients):
    dynamodb = aws_clients["dynamodb"]
    s3 = aws_clients["s3"]
    
    # Cleanup before tests
    cleanup_dynamodb_table(dynamodb, games_table_name)
    assert_table_empty(dynamodb, games_table_name)
    
    # Run the tests
    yield
    
    # Cleanup after tests
    # cleanup_dynamodb_table(dynamodb, games_table_name)
    # cleanup_s3_bucket(s3)
    # assert_table_empty(dynamodb, games_table_name)
    # assert_bucket_empty(s3, bucket_name)


def est_full_app_integration(aws_clients):
    dynamodb = aws_clients["dynamodb"]
    s3 = aws_clients["s3"]
    lambda_client = aws_clients["lambda_client"]

    # ===========================================================================
    # Begin Integration Tests
    # ===========================================================================

    # Setup S3 Dictionary
    # add_en_dictionary_to_s3(s3)
    # assert_bucket_contains(s3, constants.VALID_DICTIONARY_KEY)

    # Prepare the payload for the CreateCustomLambda function
    payload_1 = {
        "body": json.dumps({
            "gameLayout": constants.VALID_LAYOUT_1,  
            "language": constants.VALID_LANGUAGE,       
            "boardSize": constants.VALID_BOARD_SIZE     
        })
    }

    # Create a custom game
    print("Creating a valid custom game")
    create_response = lambda_client.invoke(
        FunctionName="CreateCustomLambdaTest",
        InvocationType='RequestResponse',
        Payload=json.dumps(payload_1)
    )

    # Read and parse the response payload
    response_payload = json.loads(create_response['Payload'].read())
    print("response payload:", response_payload)

    # Check for errors
    if 'FunctionError' in create_response:
        error_message = response_payload.get('errorMessage', 'Unknown error')
        pytest.fail(f"Lambda invocation failed with error: {error_message}")

    # Extract gameId from the response
    game_id = json.loads(response_payload.get('body', '{}')).get('gameId')
    assert game_id, "No gameId returned from CreateCustomLambdaTest"

    # Verify the game data in DynamoDB
    assert_dynamodb_item_exists(dynamodb, game_id)

    # Let's create a functionally equivalent game

    # Now let's fetch the game we just created using the fetch Lambda



# Cleanup resources and verify cleanup complete
def cleanup_dynamodb_table(dynamodb, table_name):
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
    print("Dictionary was found in S3 bucket.")

def assert_dynamodb_item_exists(dynamodb, game_id):
    """Assert that a specific item exists in DynamoDB."""
    table = dynamodb.Table(games_table_name)
    response = table.get_item(Key={"gameId": game_id})
    assert "Item" in response, f"Item with gameId {game_id} not found in {table}."
    print(f"Item with gameId {game_id} was found in DynamoDB table.")

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
