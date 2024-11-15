from aws_cdk import (
    Stack,
    aws_dynamodb as dynamodb,
    aws_lambda as _lambda
)
from constructs import Construct

class LetterBoxedStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

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

        # Define the validate_word Lambda function
        validate_word_lambda = _lambda.Function(
            self, "ValidateWordFunction",
            runtime=_lambda.Runtime.PYTHON_3_10,
            handler="validate_word.handler",
            code=_lambda.Code.from_asset("lambdas")
        )

        # Grant DynamoDB read/write permissions to each Lambda function
        self.game_table.grant_read_write_data(fetch_game_lambda)
        self.game_table.grant_read_write_data(create_custom_lambda)
        self.game_table.grant_read_write_data(validate_word_lambda)
