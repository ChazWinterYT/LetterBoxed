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
    Size
)
from constructs import Construct

class LetterBoxedStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, is_test=False, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ===========================================================================
        # Define DynamoDB Resources
        # ===========================================================================
        
        # Constants for table names for consistent naming
        prod_GAMES_TABLE_NAME = "LetterBoxedGames"
        prod_VALID_WORDS_TABLE_NAME = "LetterBoxedValidWords1"
        prod_SESSION_STATES_TABLE_NAME = "LetterBoxedSessionStates"
        prod_METADATA_TABLE_NAME = "LetterBoxedMetadataTable"
        prod_ARCHIVE_TABLE_NAME = "LetterBoxedNYTArchives"
        prod_RANDOM_GAMES_TABLE_NAME_EN = "LetterBoxedRandomGames_en"
        prod_RANDOM_GAMES_TABLE_NAME_ES = "LetterBoxedRandomGames_es"
        prod_RANDOM_GAMES_TABLE_NAME_IT = "LetterBoxedRandomGames_it"
        prod_RANDOM_GAMES_TABLE_NAME_PL = "LetterBoxedRandomGames_pl"
        prod_RANDOM_GAMES_TABLE_NAME_RU = "LetterBoxedRandomGames_ru"

        test_GAMES_TABLE_NAME = "LetterBoxedGamesTest"
        test_VALID_WORDS_TABLE_NAME = "LetterBoxedValidWords1Test"
        test_SESSION_STATES_TABLE_NAME = "LetterBoxedSessionStatesTest"
        test_METADATA_TABLE_NAME = "LetterBoxedMetadataTableTest"
        test_ARCHIVE_TABLE_NAME = "LetterBoxedNYTArchivesTest"
        test_RANDOM_GAMES_TABLE_NAME_EN = "LetterBoxedRandomGames_enTest"
        test_RANDOM_GAMES_TABLE_NAME_ES = "LetterBoxedRandomGames_esTest"
        test_RANDOM_GAMES_TABLE_NAME_IT = "LetterBoxedRandomGames_itTest"
        test_RANDOM_GAMES_TABLE_NAME_PL = "LetterBoxedRandomGames_plTest"
        test_RANDOM_GAMES_TABLE_NAME_RU = "LetterBoxedRandomGames_ruTest"

        # DB tables must be added to a list so Lambdas can be grated permissions to them
        prod_table_resources = []
        test_table_resources = []

        # Production DynamoDB Games table
        self.prod_game_table = dynamodb.Table.from_table_name(
            self, "LetterBoxedGamesTable",
            table_name=prod_GAMES_TABLE_NAME
        )
        prod_table_resources.append(self.prod_game_table)
        
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
        test_table_resources.append(self.test_game_table)

        # Production DynamoDB ValidWords table
        self.prod_valid_words_table = dynamodb.Table.from_table_name(
            self, "LetterBoxedValidWordsTable",
            table_name=prod_VALID_WORDS_TABLE_NAME
        )
        prod_table_resources.append(self.prod_valid_words_table)

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
        test_table_resources.append(self.test_valid_words_table)

        # Production DynamoDB SessionStates table
        self.prod_user_game_states_table = dynamodb.Table.from_table_name(
            self, "LetterBoxedSessionStatesTable",
            table_name=prod_SESSION_STATES_TABLE_NAME,
        )
        prod_table_resources.append(self.prod_user_game_states_table)

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
        test_table_resources.append(self.test_user_game_states_table)

        # Production DynamoDB Metadata table
        self.prod_metadata_table = dynamodb.Table.from_table_name(
            self, "LetterBoxedMetadataTable",
            table_name=prod_METADATA_TABLE_NAME
        )
        prod_table_resources.append(self.prod_metadata_table)

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
        test_table_resources.append(self.test_metadata_table)
        
        # Production DynamoDB Archived Games table
        self.prod_archive_table = dynamodb.Table(
            self, "LetterBoxedNYTArchivesTable",
            table_name=prod_ARCHIVE_TABLE_NAME,
            partition_key=dynamodb.Attribute(
                name="NYTGame",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="gameId",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.RETAIN
        )
        test_table_resources.append(self.prod_archive_table)

        # Test DynamoDB Archived Games table
        self.test_archive_table = dynamodb.Table(
            self, "LetterBoxedNYTArchivesTestTable",
            table_name=test_ARCHIVE_TABLE_NAME,
            partition_key=dynamodb.Attribute(
                name="NYTGame",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="gameId",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )
        test_table_resources.append(self.test_archive_table)

        # Production Random Games Tables in various languages
        # English
        self.prod_random_games_table_en = dynamodb.Table(
            self, "LetterBoxedRandomGamesTable_en",
            table_name=prod_RANDOM_GAMES_TABLE_NAME_EN,
            partition_key=dynamodb.Attribute(
                name="atomicNumber",
                type=dynamodb.AttributeType.NUMBER
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.RETAIN
        )
        prod_table_resources.append(self.prod_random_games_table_en)

        # Spanish
        self.prod_random_games_table_es = dynamodb.Table(
            self, "LetterBoxedRandomGamesTable_es",
            table_name=prod_RANDOM_GAMES_TABLE_NAME_ES,
            partition_key=dynamodb.Attribute(
                name="atomicNumber",
                type=dynamodb.AttributeType.NUMBER
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.RETAIN
        )
        prod_table_resources.append(self.prod_random_games_table_es)

        # Italian
        self.prod_random_games_table_it = dynamodb.Table(
            self, "LetterBoxedRandomGamesTable_it",
            table_name=prod_RANDOM_GAMES_TABLE_NAME_IT,
            partition_key=dynamodb.Attribute(
                name="atomicNumber",
                type=dynamodb.AttributeType.NUMBER
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.RETAIN
        )
        prod_table_resources.append(self.prod_random_games_table_it)

        # Polish
        self.prod_random_games_table_pl = dynamodb.Table(
            self, "LetterBoxedRandomGamesTable_pl",
            table_name=prod_RANDOM_GAMES_TABLE_NAME_PL,
            partition_key=dynamodb.Attribute(
                name="atomicNumber",
                type=dynamodb.AttributeType.NUMBER
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.RETAIN
        )
        prod_table_resources.append(self.prod_random_games_table_pl)

        # Russian
        self.prod_random_games_table_ru = dynamodb.Table(
            self, "LetterBoxedRandomGamesTable_ru",
            table_name=prod_RANDOM_GAMES_TABLE_NAME_RU,
            partition_key=dynamodb.Attribute(
                name="atomicNumber",
                type=dynamodb.AttributeType.NUMBER
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.RETAIN
        )
        prod_table_resources.append(self.prod_random_games_table_ru)

        # Test Random Games Tables in various languages
        #English
        self.test_random_games_table_en = dynamodb.Table(
            self, "LetterBoxedRandomGamesTestTable_en",
            table_name=test_RANDOM_GAMES_TABLE_NAME_EN,
            partition_key=dynamodb.Attribute(
                name="atomicNumber",
                type=dynamodb.AttributeType.NUMBER
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )
        test_table_resources.append(self.test_random_games_table_en)

        # Spanish
        self.test_random_games_table_es = dynamodb.Table(
            self, "LetterBoxedRandomGamesTestTable_es",
            table_name=test_RANDOM_GAMES_TABLE_NAME_ES,
            partition_key=dynamodb.Attribute(
                name="atomicNumber",
                type=dynamodb.AttributeType.NUMBER
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )
        test_table_resources.append(self.test_random_games_table_es)

        # Italian
        self.test_random_games_table_it = dynamodb.Table(
            self, "LetterBoxedRandomGamesTestTable_it",
            table_name=test_RANDOM_GAMES_TABLE_NAME_IT,
            partition_key=dynamodb.Attribute(
                name="atomicNumber",
                type=dynamodb.AttributeType.NUMBER
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )
        test_table_resources.append(self.test_random_games_table_it)

        # Polish
        self.test_random_games_table_pl = dynamodb.Table(
            self, "LetterBoxedRandomGamesTestTable_pl",
            table_name=test_RANDOM_GAMES_TABLE_NAME_PL,
            partition_key=dynamodb.Attribute(
                name="atomicNumber",
                type=dynamodb.AttributeType.NUMBER
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )
        test_table_resources.append(self.test_random_games_table_pl)

        # Russian
        self.test_random_games_table_ru = dynamodb.Table(
            self, "LetterBoxedRandomGamesTestTable_ru",
            table_name=test_RANDOM_GAMES_TABLE_NAME_RU,
            partition_key=dynamodb.Attribute(
                name="atomicNumber",
                type=dynamodb.AttributeType.NUMBER
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )
        test_table_resources.append(self.test_random_games_table_ru)

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
        prod_common_environment = {
            "GAMES_TABLE": prod_GAMES_TABLE_NAME,
            "VALID_WORDS_TABLE": prod_VALID_WORDS_TABLE_NAME,
            "SESSION_STATES_TABLE": prod_SESSION_STATES_TABLE_NAME,
            "RANDOM_GAMES_TABLE_EN": prod_RANDOM_GAMES_TABLE_NAME_EN,
            "RANDOM_GAMES_TABLE_ES": prod_RANDOM_GAMES_TABLE_NAME_ES,
            "RANDOM_GAMES_TABLE_IT": prod_RANDOM_GAMES_TABLE_NAME_IT,
            "RANDOM_GAMES_TABLE_PL": prod_RANDOM_GAMES_TABLE_NAME_PL,
            "RANDOM_GAMES_TABLE_RU": prod_RANDOM_GAMES_TABLE_NAME_RU,
            "METADATA_TABLE": prod_METADATA_TABLE_NAME,
            "ARCHIVE_TABLE": prod_ARCHIVE_TABLE_NAME,
            "DICTIONARY_SOURCE": "s3",
            "S3_BUCKET_NAME": "chazwinter.com",
            "DICTIONARY_BASE_S3_PATH": "LetterBoxed/Dictionaries/",
            "DEFAULT_LANGUAGE": "en",
        }
        
        test_common_environment = {
            "GAMES_TABLE": test_GAMES_TABLE_NAME,
            "VALID_WORDS_TABLE": test_VALID_WORDS_TABLE_NAME,
            "SESSION_STATES_TABLE": test_SESSION_STATES_TABLE_NAME,
            "RANDOM_GAMES_TABLE_EN": test_RANDOM_GAMES_TABLE_NAME_EN,
            "RANDOM_GAMES_TABLE_ES": test_RANDOM_GAMES_TABLE_NAME_ES,
            "RANDOM_GAMES_TABLE_IT": test_RANDOM_GAMES_TABLE_NAME_IT,
            "RANDOM_GAMES_TABLE_PL": test_RANDOM_GAMES_TABLE_NAME_PL,
            "RANDOM_GAMES_TABLE_RU": test_RANDOM_GAMES_TABLE_NAME_RU,
            "METADATA_TABLE": test_METADATA_TABLE_NAME,
            "ARCHIVE_TABLE": test_ARCHIVE_TABLE_NAME,
            "DICTIONARY_SOURCE": "s3",
            "S3_BUCKET_NAME": "test-dictionary-bucket",
            "DICTIONARY_BASE_S3_PATH": "Dictionaries/",
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
            "fetch_user_state": {
                "handler": "lambdas.fetch_user_state.handler.handler",
                "name": "FetchUserStateLambda"
            },
            "save_user_state": {
                "handler": "lambdas.save_user_state.handler.handler",
                "name": "SaveUserStateLambda"
            }
        }

        # Create Lambda layer for dependencies
        lambda_layer = _lambda.LayerVersion(
            self, "LambdaLayerRequests",
            code=_lambda.Code.from_asset("lambda_layer"),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_10],
            description="Lambda layer that includes dependency libraries."
        )

        # Create Lambda functions and store references to them,
        # so they can be used when creating API routing
        lambda_references = {}
        for lambda_key, lambda_config in lambda_functions.items():
            # Create Production Lambda
            prod_lambda = self.create_lambda(
                lambda_key, 
                lambda_config, 
                prod_common_environment, 
                "", 
                lambda_layer, 
                prod_table_resources
            )
            # Grant each Lambda S3 read access
            self.prod_bucket.grant_read(prod_lambda)
            # Save Lambda names for routing with API. Needed for prod only.
            lambda_references[lambda_key] = prod_lambda 

            # Create Test Lambda
            test_lambda = self.create_lambda(
                lambda_key, 
                lambda_config, 
                test_common_environment, 
                "Test", 
                lambda_layer, 
                test_table_resources
            )
            # Grant each test Lambda S3 read access to the test bucket
            self.test_bucket.grant_read(test_lambda)


        # ===========================================================================
        # Define API Gateway REST API Resources
        # ===========================================================================
        api = apigateway.RestApi(
            self, "LetterBoxedApi",
            rest_api_name="LetterBoxed Service",
            description="This service handles functions related to the LetterBoxed game"
        )
        
        # Helper function to enable CORS
        def add_cors(resource):
            """
            Add CORS support by creating an OPTIONS method for the given resource.
            """
            resource.add_method(
                "OPTIONS",
                apigateway.MockIntegration(
                    integration_responses=[
                        {
                            "statusCode": "200",
                            "responseParameters": {
                                "method.response.header.Access-Control-Allow-Headers": "'Content-Type,Authorization'",
                                "method.response.header.Access-Control-Allow-Methods": "'OPTIONS,GET,POST,PUT'",
                                "method.response.header.Access-Control-Allow-Origin": "'*'",
                            },
                        },
                    ],
                    passthrough_behavior=apigateway.PassthroughBehavior.NEVER,
                    request_templates={"application/json": '{"statusCode": 200}'},
                ),
                method_responses=[
                    {
                        "statusCode": "200",
                        "responseParameters": {
                            "method.response.header.Access-Control-Allow-Headers": True,
                            "method.response.header.Access-Control-Allow-Methods": True,
                            "method.response.header.Access-Control-Allow-Origin": True,
                        },
                    }
                ],
            )

        
        # Set up /games resource and methods
        games_resource = api.root.add_resource("games")
        
        # GET /games/{gameId} - Fetch an existing game
        game_id_resource = games_resource.add_resource("{gameId}")
        game_id_resource.add_method(
            "GET",
            apigateway.LambdaIntegration(lambda_references["fetch_game"])
        )
        add_cors(game_id_resource)
        
        # POST /games - Create a custom game
        games_resource.add_method(
            "POST",
            apigateway.LambdaIntegration(lambda_references["create_custom"])
        )
        add_cors(games_resource)
        
        # Set up /validate resource and POST method
        validate_integration = apigateway.LambdaIntegration(lambda_references["validate_word"])
        validate_resource = api.root.add_resource("validate")
        validate_resource.add_method("POST", validate_integration)
        add_cors(validate_resource)
        
        # Route for prefetch_todays_game
        prefetch_integration = apigateway.LambdaIntegration(lambda_references["prefetch_todays_game"])
        prefetch_resource = api.root.add_resource("prefetch")
        prefetch_resource.add_method("GET", prefetch_integration)
        add_cors(prefetch_resource)
        
        # Route for play_today Lambda
        play_today_integration = apigateway.LambdaIntegration(lambda_references["play_today"])
        play_today_resource = api.root.add_resource("play-today")
        play_today_resource.add_method("GET", play_today_integration)
        add_cors(play_today_resource)

        # Route for game_archive Lambda
        game_archive_integration = apigateway.LambdaIntegration(lambda_references["game_archive"])
        game_archive_resource = api.root.add_resource("archive")
        game_archive_resource.add_method("GET", game_archive_integration)
        add_cors(game_archive_resource)
        
        # GET /random-game - Fetch a random game
        random_game_resource = api.root.add_resource("random-game")
        random_game_resource.add_method(
            "GET",
            apigateway.LambdaIntegration(lambda_references["fetch_random"])
        )
        # POST /random-game - Create a random game
        random_game_resource.add_method(
            "POST",
            apigateway.LambdaIntegration(lambda_references["create_random"])
        )
        add_cors(random_game_resource)
        
        # Set up sessions resource
        sessions_resource = api.root.add_resource("sessions")
        session_id_resource = sessions_resource.add_resource("{sessionId}")
        
        # GET /sessions/{sessionId}?gameId={gameId} - Fetch a user's game state
        session_id_resource.add_method(
            "GET",
            apigateway.LambdaIntegration(lambda_references["fetch_user_state"])
        )
        # PUT /sessions/{sessionId}?gameId={gameId} - Update a user's game state
        session_id_resource.add_method(
            "PUT",
            apigateway.LambdaIntegration(lambda_references["save_user_state"])
        )
        add_cors(session_id_resource)


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
                    "dictionaries",
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
            timeout=Duration.seconds(120),
            memory_size=1024,
            ephemeral_storage_size=Size.gibibytes(2),
            layers=[layer],
            environment=environment,
            function_name=lambda_config["name"] + function_suffix
        )
        # Grant resources to the Lambda
        for resource in resources:
            resource.grant_read_write_data(lambda_function)
        return lambda_function
