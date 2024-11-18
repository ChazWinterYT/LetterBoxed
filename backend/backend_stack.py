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
            table_name="LetterBoxedValidWords",
            partition_key=dynamodb.Attribute(
                name="gameId",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="word",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.RETAIN
        )

        # Test ValidWords DynamoDB table
        self.test_valid_words_table = dynamodb.Table(
            self, "LetterBoxedValidWordsTestTable",
            table_name="LetterBoxedValidWordsTest",
            partition_key=dynamodb.Attribute(
                name="gameId",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="word",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )

        # Production UserGameStates DynamoDB table
        self.prod_user_game_states_table = dynamodb.Table(
            self, "LetterBoxedUserGameStatesTable",
            table_name="LetterBoxedUserGameStates",
            partition_key=dynamodb.Attribute(
                name="userId",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="gameId",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.RETAIN
        )

        # Test UserGameStates DynamoDB table
        self.test_user_game_states_table = dynamodb.Table(
            self, "LetterBoxedUserGameStatesTestTable",
            table_name="LetterBoxedUserGameStatesTest",
            partition_key=dynamodb.Attribute(
                name="userId",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="gameId",
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

        CfnOutput(self, "DictionaryBucketName", value=self.prod_bucket.bucket_name)


        # ===========================================================================
        # Define Lambda Functions
        # ===========================================================================
        # Define table and bucket names based on the environment
        game_table_name = "LetterBoxedGamesTest" if is_test else "LetterBoxedGames"
        dictionary_bucket_name = "test-dictionary-bucket" if is_test else "chazwinter.com"
        valid_words_table_name = "LetterBoxedValidWordsTest" if is_test else "LetterBoxedValidWords"
        user_game_states_table_name = "LetterBoxedUserGameStatesTest" if is_test else "LetterBoxedUserGameStates"

        # Define common environment for all Lambdas
        common_environment = {
            "GAME_TABLE": game_table_name,
            "VALID_WORDS_TABLE": valid_words_table_name,
            "USER_GAME_STATES_TABLE": user_game_states_table_name,
            "DICTIONARY_SOURCE": "s3",
            "S3_BUCKET_NAME": dictionary_bucket_name,
            "DICTIONARY_BASE_S3_PATH": "Dictionaries/",
            "DEFAULT_LANGUAGE": "en",
        }

        # Define the Lambda function handlers and their respective names
        lambda_functions = {
            "fetch_game": {
                "handler": "fetch_game.handler",
                "name": "FetchGameLambda"
            },
            "create_custom": {
                "handler": "create_custom.handler",
                "name": "CreateCustomLambda"
            },
            "prefetch_todays_game": {
                "handler": "prefetch_todays_game.handler",
                "name": "PrefetchTodaysGameLambda"
            },
            "play_today": {
                "handler": "play_today.handler",
                "name": "PlayTodayLambda"
            },
            "validate_word": {
                "handler": "validate_word.handler",
                "name": "ValidateWordLambda"
            },
            "game_archive": {
                "handler": "game_archive.handler",
                "name": "GameArchiveLambda"
            },
        }

        # Create Lambda functions and store references to them,
        # so they can be used when creating API routing
        lambda_references = {}
        for lambda_key, lambda_config in lambda_functions.items():
            lambda_function = _lambda.Function(
                self, lambda_config["name"],
                runtime=_lambda.Runtime.PYTHON_3_10,
                handler=lambda_config["handler"],
                code=_lambda.Code.from_asset("lambdas"),
                environment=common_environment,
                function_name=lambda_config["name"]
            )
            self.test_game_table.grant_read_write_data(lambda_function)
            self.prod_game_table.grant_read_write_data(lambda_function)
            self.test_bucket.grant_read(lambda_function)
            self.prod_bucket.grant_read(lambda_function)
            self.test_valid_words_table.grant_read_write_data(lambda_function)
            self.prod_valid_words_table.grant_read_write_data(lambda_function)
            self.test_user_game_states_table.grant_read_write_data(lambda_function)
            self.prod_user_game_states_table.grant_read_write_data(lambda_function)
            lambda_references[lambda_key] = lambda_function


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
