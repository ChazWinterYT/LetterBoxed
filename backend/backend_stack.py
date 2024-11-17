from aws_cdk import (
    Stack,
    aws_dynamodb as dynamodb,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
)
from constructs import Construct

class LetterBoxedStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ===============================================================================
        # Define DynamoDB Resources
        # ===============================================================================

        # DynamoDB table definition for unique games and standardized solutions
        self.game_table = dynamodb.Table(
            self, "LetterBoxedGamesTable",
            table_name="LetterBoxedGames",
            partition_key=dynamodb.Attribute(
                name="gameId",          # Unique identifier for each specific game layout
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST
        )

        # Global Secondary Index (GSI) for standardized game layouts (equivalent solutions)
        self.game_table.add_global_secondary_index(
            index_name="StandardizedHashIndex",
            partition_key=dynamodb.Attribute(
                name="standardizedHash",  # Unique identifier for the standardized version of the layout
                type=dynamodb.AttributeType.STRING
            )
        )

        # ===============================================================================
        # Define Lambda Functions
        # ===============================================================================

        # Define the fetch_game Lambda function
        fetch_game_lambda = _lambda.Function(
            self, "FetchGameFunction",
            runtime=_lambda.Runtime.PYTHON_3_10,
            handler="fetch_game.handler",
            code=_lambda.Code.from_asset("lambdas")
        )

        # Define the create_custom Lambda function
        create_custom_lambda = _lambda.Function(
            self, "CreateCustomGameFunction",
            runtime=_lambda.Runtime.PYTHON_3_10,
            handler="create_custom.handler",
            code=_lambda.Code.from_asset("lambdas")
        )

        # Define the prefetch_todays_game Lambda function
        prefetch_todays_game_lambda = _lambda.Function(
            self, "PrefetchTodaysGameFunction",
            runtime=_lambda.Runtime.PYTHON_3_10,
            handler="prefetch_todays_game.handler",
            code=_lambda.Code.from_asset("lambdas")
        )

        # Define the play_today Lambda function
        play_today_lambda = _lambda.Function(
            self, "PlayTodayFunction",
            runtime=_lambda.Runtime.PYTHON_3_10,
            handler="play_today.handler",
            code=_lambda.Code.from_asset("lambdas")
        )

        # Define the validate_word Lambda function
        validate_word_lambda = _lambda.Function(
            self, "ValidateWordFunction",
            runtime=_lambda.Runtime.PYTHON_3_10,
            handler="validate_word.handler",
            code=_lambda.Code.from_asset("lambdas")
        )

        # Define the game_archive Lambda function
        game_archive_lambda = _lambda.Function(
            self, "GameArchiveFunction",
            runtime=_lambda.Runtime.PYTHON_3_10,
            handler="game_archive.handler",
            code=_lambda.Code.from_asset("lambdas")
        )

        # Grant DynamoDB read/write permissions to each Lambda function
        self.game_table.grant_read_write_data(fetch_game_lambda)
        self.game_table.grant_read_write_data(create_custom_lambda)
        self.game_table.grant_read_write_data(prefetch_todays_game_lambda)
        self.game_table.grant_read_write_data(play_today_lambda)
        self.game_table.grant_read_write_data(validate_word_lambda)
        self.game_table.grant_read_write_data(game_archive_lambda)


        # ===============================================================================
        # Define API Gateway REST API Resources
        # ===============================================================================
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
            apigateway.LambdaIntegration(fetch_game_lambda)
        )
        
        # POST /games - Create a custom game
        games_resource.add_method(
            "POST",
            apigateway.LambdaIntegration(create_custom_lambda)
        )
        
        # Set up /validate resource and POST method
        validate_integration = apigateway.LambdaIntegration(validate_word_lambda)
        validate_resource = api.root.add_resource("validate")
        validate_resource.add_method("POST", validate_integration)
        
        # Route for prefetch_todays_game
        prefetch_integration = apigateway.LambdaIntegration(prefetch_todays_game_lambda)
        prefetch_resource = api.root.add_resource("prefetch")
        prefetch_resource.add_method("GET", prefetch_integration)
        
        # Route for play_today Lambda
        play_today_integration = apigateway.LambdaIntegration(play_today_lambda)
        play_today_resource = api.root.add_resource("play-today")
        play_today_resource.add_method("GET", play_today_integration)

        # Route for game_archive Lambda
        game_archive_integration = apigateway.LambdaIntegration(game_archive_lambda)
        game_archive_resource = api.root.add_resource("archive")
        game_archive_resource.add_method("GET", game_archive_integration)
