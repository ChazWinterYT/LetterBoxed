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
        
        # Test DynamoDB table
        self.test_game_table = dynamodb.Table(
            self, "LetterBoxedGamesTestTable",
            table_name="LetterBoxedGamesTest",
            partition_key=dynamodb.Attribute(
                name="gameId",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY  # Test resources should be cleaned up
        )

        self.test_game_table.add_global_secondary_index(
            index_name="StandardizedHashIndex",
            partition_key=dynamodb.Attribute(
                name="standardizedHash",
                type=dynamodb.AttributeType.STRING
            )
        )

        # Production DynamoDB table
        self.prod_game_table = dynamodb.Table(
            self, "LetterBoxedGamesTable",
            table_name="LetterBoxedGames",
            partition_key=dynamodb.Attribute(
                name="gameId",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.RETAIN  # Retain production resources
        )

        self.prod_game_table.add_global_secondary_index(
            index_name="StandardizedHashIndex",
            partition_key=dynamodb.Attribute(
                name="standardizedHash",
                type=dynamodb.AttributeType.STRING
            )
        )

        # Production ValidWords DynamoDB table
        self.prod_valid_words_table = dynamodb.Table(
            self, "LetterBoxedValidWordsTable",
            table_name="LetterBoxedValidWords1",
            partition_key=dynamodb.Attribute(
                name="gameId",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.RETAIN
        )

        # Test ValidWords DynamoDB table
        self.test_valid_words_table = dynamodb.Table(
            self, "LetterBoxedValidWordsTestTable",
            table_name="LetterBoxedValidWords1Test",
            partition_key=dynamodb.Attribute(
                name="gameId",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )

        # Production SessionStates DynamoDB table
        self.prod_user_game_states_table = dynamodb.Table(
            self, "LetterBoxedSessionStatesTable",
            table_name="LetterBoxedSessionStates",
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

        # Test SessionStates DynamoDB table
        self.test_user_game_states_table = dynamodb.Table(
            self, "LetterBoxedSessionStatesTestTable",
            table_name="LetterBoxedSessionStatesTest",
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
            "GAMES_TABLE_NAME": "LetterBoxedGamesTest",
            "VALID_WORDS_TABLE": "LetterBoxedValidWords1Test",
            "SESSION_STATES_TABLE": "LetterBoxedSessionStatesTest",
            "DICTIONARY_SOURCE": "s3",
            "S3_BUCKET_NAME": "test-dictionary-bucket",
            "DICTIONARY_BASE_S3_PATH": "Dictionaries/",
            "DEFAULT_LANGUAGE": "en",
        }

        prod_common_environment = {
            "GAMES_TABLE_NAME": "LetterBoxedGames",
            "VALID_WORDS_TABLE": "LetterBoxedValidWords",
            "SESSION_STATES_TABLE": "LetterBoxedSessionStates",
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
            "create_custom": {
                "handler": "lambdas.create_custom.handler.handler",
                "name": "CreateCustomLambda"
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
                self.prod_user_game_states_table
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
                self.test_user_game_states_table
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
        api = apigateway.RestApi(
            self, "LetterBoxedApi",
            rest_api_name="LetterBoxed Service",
            description="This service handles functions related to the LetterBoxed game"
        )
        
        # Set up /games resource and methods
        games_resource = api.root.add_resource("games")
        
        # GET /games/{gameId} - Fetch an existing game
        game_id_resource = games_resource.add_resource("{gameId}")
        game_id_resource.add_method(
            "GET",
            apigateway.LambdaIntegration(lambda_references["fetch_game"])
        )
        
        # POST /games - Create a custom game
        games_resource.add_method(
            "POST",
            apigateway.LambdaIntegration(lambda_references["create_custom"])
        )
        
        # Set up /validate resource and POST method
        validate_integration = apigateway.LambdaIntegration(lambda_references["validate_word"])
        validate_resource = api.root.add_resource("validate")
        validate_resource.add_method("POST", validate_integration)
        
        # Route for prefetch_todays_game
        prefetch_integration = apigateway.LambdaIntegration(lambda_references["prefetch_todays_game"])
        prefetch_resource = api.root.add_resource("prefetch")
        prefetch_resource.add_method("GET", prefetch_integration)
        
        # Route for play_today Lambda
        play_today_integration = apigateway.LambdaIntegration(lambda_references["play_today"])
        play_today_resource = api.root.add_resource("play-today")
        play_today_resource.add_method("GET", play_today_integration)

        # Route for game_archive Lambda
        game_archive_integration = apigateway.LambdaIntegration(lambda_references["game_archive"])
        game_archive_resource = api.root.add_resource("archive")
        game_archive_resource.add_method("GET", game_archive_integration)


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
