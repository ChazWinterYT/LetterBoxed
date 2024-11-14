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

        # Lambda function for word validation
        self.validate_word_function = _lambda.Function(
            self, "ValidateWordFunction",
            runtime=_lambda.Runtime.PYTHON_3_10,
            handler="validate_word.handler",
            code=_lambda.Code.from_asset("lambda")
        )

        # Grant read/write permissions to the Lambda function
        self.game_table.grant_read_write_data(self.validate_word_function)
