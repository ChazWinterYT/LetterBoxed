import os
import glob
import boto3
from aws_cdk import (
    Stack,
    aws_dynamodb as dynamodb,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_s3 as s3,
    CfnOutput,
    RemovalPolicy,
    Duration,
)
from constructs import Construct

class LetterBoxedStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, is_test=False, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ===========================================================================
        # Define DynamoDB Resources
        # ===========================================================================
        
        prod_GAMES_TABLE_NAME = "LetterBoxedGames"
        prod_VALID_WORDS_TABLE_NAME = "LetterBoxedValidWords1"
        prod_SESSION_STATES_TABLE_NAME = "LetterBoxedSessionStates"
        prod_RANDOM_GAMES_TABLE_NAME = "LetterBoxedRandomGames"
        prod_METADATA_TABLE_NAME = "LetterBoxedMetadataTable"
        test_GAMES_TABLE_NAME = "LetterBoxedGamesTest"
        test_VALID_WORDS_TABLE_NAME = "LetterBoxedValidWords1Test"
        test_SESSION_STATES_TABLE_NAME = "LetterBoxedSessionStatesTest"
        test_RANDOM_GAMES_TABLE_NAME = "LetterBoxedRandomGamesTest"
        test_METADATA_TABLE_NAME = "LetterBoxedMetadataTableTest"

        # Test DynamoDB Games table
        self.test_game_table = dynamodb.Table(
            self, "LetterBoxedGamesTestTable",
            table_name=test_GAMES_TABLE_NAME,
            partition_key=dynamodb.Attribute(
                name="gameId",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY  # Test resources should be cleaned up
        )

        # Production DynamoDB Games table
        self.prod_game_table = dynamodb.Table(
            self, "LetterBoxedGamesTable",
            table_name=prod_GAMES_TABLE_NAME,
            partition_key=dynamodb.Attribute(
                name="gameId",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.RETAIN  # Retain production resources
        )

        # Production DynamoDB ValidWords table
        self.prod_valid_words_table = dynamodb.Table(
            self, "LetterBoxedValidWordsTable",
            table_name=prod_VALID_WORDS_TABLE_NAME,
            partition_key=dynamodb.Attribute(
                name="gameId",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.RETAIN
        )

        # Test DynamoDB ValidWords table
        self.test_valid_words_table = dynamodb.Table(
            self, "LetterBoxedValidWordsTestTable",
            table_name=test_VALID_WORDS_TABLE_NAME,
            partition_key=dynamodb.Attribute(
                name="gameId",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )

        # Production DynamoDB SessionStates table
        self.prod_user_game_states_table = dynamodb.Table(
            self, "LetterBoxedSessionStatesTable",
            table_name=prod_SESSION_STATES_TABLE_NAME,
            partition_key=dynamodb.Attribute(
                name="sessionId",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="gameId",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.RETAIN,
            time_to_live_attribute="TTL"
        )

        # Test DynamoDB SessionStates table
        self.test_user_game_states_table = dynamodb.Table(
            self, "LetterBoxedSessionStatesTestTable",
            table_name=test_SESSION_STATES_TABLE_NAME,
            partition_key=dynamodb.Attribute(
                name="sessionId",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="gameId",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
            time_to_live_attribute="TTL"
        )

        # Production DynamoDB RandomGames table
        self.prod_random_games_table = dynamodb.Table(
            self, "LetterBoxedRandomGamesTable",
            table_name=prod_RANDOM_GAMES_TABLE_NAME,
            partition_key=dynamodb.Attribute(
                name="atomicNumber",
                type=dynamodb.AttributeType.NUMBER
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.RETAIN
        )

        # Test DynamoDB RandomGames table
        self.test_random_games_table = dynamodb.Table(
            self, "LetterBoxedRandomGamesTestTable",
            table_name=test_RANDOM_GAMES_TABLE_NAME,
            partition_key=dynamodb.Attribute(
                name="atomicNumber",
                type=dynamodb.AttributeType.NUMBER
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )

        # Production DynamoDB Metadata table
        self.prod_metadata_table = dynamodb.Table(
            self, "LetterBoxedMetadataTable",
            table_name=prod_METADATA_TABLE_NAME,
            partition_key=dynamodb.Attribute(
                name="metadataType",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.RETAIN
        )

        # Test DynamoDB Metadata table
        self.test_metadata_table = dynamodb.Table(
            self, "LetterBoxedMetadataTestTable",
            table_name=test_METADATA_TABLE_NAME,
            partition_key=dynamodb.Attribute(
                name="metadataType",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )


        # ===========================================================================
        # Define S3 Resources
        # ===========================================================================

        # Test S3 bucket
        self.test_bucket = s3.Bucket.from_bucket_name(
            self, "TestDictionariesBucket",
            bucket_name="test-dictionary-bucket"
        )

        # Production S3 bucket (referencing an existing bucket)
        self.prod_bucket = s3.Bucket.from_bucket_name(
            self, "DictionariesBucket",
            bucket_name="chazwinter.com"
        )

        CfnOutput(self, "TestDictionaryBucketName", value=self.test_bucket.bucket_name)
        CfnOutput(self, "DictionaryBucketName", value=self.prod_bucket.bucket_name)


        # ===========================================================================
        # Define Lambda Functions
        # ===========================================================================

        # Define common environment for all Lambdas
        test_common_environment = {
            "GAMES_TABLE_NAME": test_GAMES_TABLE_NAME,
            "VALID_WORDS_TABLE": test_VALID_WORDS_TABLE_NAME,
            "SESSION_STATES_TABLE": test_SESSION_STATES_TABLE_NAME,
            "RANDOM_GAMES_TABLE": test_RANDOM_GAMES_TABLE_NAME,
            "METADATA_TABLE": test_METADATA_TABLE_NAME,
            "DICTIONARY_SOURCE": "s3",
            "S3_BUCKET_NAME": "test-dictionary-bucket",
            "DICTIONARY_BASE_S3_PATH": "Dictionaries/",
            "DEFAULT_LANGUAGE": "en",
        }

        prod_common_environment = {
            "GAMES_TABLE_NAME": prod_GAMES_TABLE_NAME,
            "VALID_WORDS_TABLE": prod_VALID_WORDS_TABLE_NAME,
            "SESSION_STATES_TABLE": prod_SESSION_STATES_TABLE_NAME,
            "RANDOM_GAMES_TABLE": prod_RANDOM_GAMES_TABLE_NAME,
            "METADATA_TABLE": prod_METADATA_TABLE_NAME,
            "DICTIONARY_SOURCE": "s3",
            "S3_BUCKET_NAME": "chazwinter.com",
            "DICTIONARY_BASE_S3_PATH": "LetterBoxed/Dictionaries/",
            "DEFAULT_LANGUAGE": "en",
        }

        # Define the Lambda function handlers and their respective names
        lambda_functions = {
            "fetch_game": {
                "handler": "lambdas.fetch_game.handler.handler",
                "name": "FetchGameLambda"
            },
            "fetch_random": {
                "handler": "lambdas.fetch_random.handler.handler",
                "name": "FetchRandomGameLambda"
            },
            "create_custom": {
                "handler": "lambdas.create_custom.handler.handler",
                "name": "CreateCustomLambda"
            },
            "create_random": {
                "handler": "lambdas.create_random.handler.handler",
                "name": "CreateRandomGameLambda"
            },
            "prefetch_todays_game": {
                "handler": "lambdas.prefetch_todays_game.handler.handler",
                "name": "PrefetchTodaysGameLambda"
            },
            "play_today": {
                "handler": "lambdas.play_today.handler.handler",
                "name": "PlayTodayLambda"
            },
            "validate_word": {
                "handler": "lambdas.validate_word.handler.handler",
                "name": "ValidateWordLambda"
            },
            "game_archive": {
                "handler": "lambdas.game_archive.handler.handler",
                "name": "GameArchiveLambda"
            },
        }

        # Create Lambda layer for dependencies
        lambda_layer = _lambda.LayerVersion(
            self, "LambdaLayerRequests",
            code=_lambda.Code.from_asset("lambda_layer"),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_10],
            description="Lambda layer that includes the requests library."
        )

        # Create Lambda functions and store references to them,
        # so they can be used when creating API routing
        lambda_references = {}
        for lambda_key, lambda_config in lambda_functions.items():
            # Create Production Lambda
            prod_resources = [
                self.prod_game_table, 
                self.prod_valid_words_table, 
                self.prod_user_game_states_table,
                self.prod_random_games_table,
                self.prod_metadata_table
            ]
            prod_lambda = self.create_lambda(
                lambda_key, 
                lambda_config, 
                prod_common_environment, 
                "", 
                lambda_layer, 
                prod_resources
            )
            self.prod_bucket.grant_read(prod_lambda)
            lambda_references[lambda_key] = prod_lambda # Needed for prod only

            # Create Test Lambda
            test_resources = [
                self.test_game_table, 
                self.test_valid_words_table, 
                self.test_user_game_states_table,
                self.test_random_games_table,
                self.test_metadata_table
            ]
            test_lambda = self.create_lambda(
                lambda_key, 
                lambda_config, 
                test_common_environment, 
                "Test", 
                lambda_layer, 
                test_resources
            )
            self.test_bucket.grant_read(test_lambda)


        # ===========================================================================
        # Define API Gateway REST API Resources
        # ===========================================================================
        
        # Define API Gateway REST API
        api = apigateway.RestApi(
            self, "LetterBoxedApi",
            rest_api_name="LetterBoxed Service",
            description="This service handles functions related to the LetterBoxed game",
        )
        
        # Resources and Methods
        # /games/{gameId} - Fetch an existing game
        add_api_method(api.root, "games/{gameId}", "GET", lambda_references["fetch_game"])

        # /random-game - Fetch a random game
        add_api_method(api.root, "random-game", "GET", lambda_references["fetch_random"])

        # /custom-game - Create a custom game
        add_api_method(api.root, "custom-game", "POST", lambda_references["create_custom"])

        # /random-game - Create a new random game
        add_api_method(api.root, "random-game", "POST", lambda_references["create_random"])

        # /prefetch-today - Prefetch today's NYT game
        add_api_method(api.root, "prefetch-today", "GET", lambda_references["prefetch_todays_game"])

        # /play-today - Play today's NYT game
        add_api_method(api.root, "play-today", "GET", lambda_references["play_today"])

        # /validate - Validate a word
        add_api_method(api.root, "validate", "POST", lambda_references["validate_word"])

        # /archive - Fetch the archive of games
        add_api_method(api.root, "archive", "GET", lambda_references["game_archive"])


    # Helper function to create a resource with methods
    def add_api_method(api_root, path: str, method: str, lambda_ref, cors=True):
        """
        Adds a resource and method to the API Gateway.

        Args:
            api_root: The root or parent resource.
            path (str): The resource path.
            method (str): HTTP method (e.g., "GET", "POST").
            lambda_ref: The Lambda function reference.
            cors (bool): Whether to enable CORS for this resource.

        Returns:
            The created resource.
        """
        resource = api_root.add_resource(path)
        integration = apigateway.LambdaIntegration(lambda_ref)
        resource.add_method(
            method,
            integration,
            method_responses=[
                {
                    "statusCode": "200",
                    "responseParameters": {
                        "method.response.header.Access-Control-Allow-Origin": True,
                    },
                }
            ] if cors else []
        )
        # Add CORS options if enabled
        if cors:
            apigateway.Cors.add_cors_options(resource, allow_origins=["*"])
        return resource


    def create_lambda(self, lambda_key, lambda_config, environment, function_suffix, layer, resources):
        lambda_function = _lambda.Function(
            self, lambda_config["name"] + function_suffix,
            runtime=_lambda.Runtime.PYTHON_3_10,
            handler=lambda_config["handler"],
            code=_lambda.Code.from_asset(
                path=".",
                exclude=[
                    "**/node_modules",
                    "**/__pycache__",
                    ".pytest_cache",
                    "**/.git",
                    "**/.idea",
                    "**/.vscode",
                    "**/*.pyc",
                    "cdk.out",
                    "venv",
                    "lambda_layer",
                    "*.iml",
                    "*.log",
                    "*.tmp",
                    "*.zip",
                    "*.tar.gz",
                    ".env",
                    ".gitignore",
                    "utility",
                    "test",
                    "cdk.json",
                    "*.bat",
                    "*.md"
                ],
            ),
            timeout=Duration.seconds(60),
            layers=[layer],
            environment=environment,
            function_name=lambda_config["name"] + function_suffix
        )
        # Grant resources to the Lambda
        for resource in resources:
            resource.grant_read_write_data(lambda_function)
        return lambda_function
