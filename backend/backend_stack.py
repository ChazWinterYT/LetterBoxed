from aws_cdk import (
    Stack,
    aws_sqs as sqs,
    aws_dynamodb as dynamodb
)
from constructs import Construct

class LetterBoxedStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # DynamoDB table definition
        self.game_table = dynamodb.Table(
            self, "LetterBoxedGamesTable",
            partition_key=dynamodb.Attribute(
                name="gameid",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST
        )
        # Global Secondary Index for userid
        self.game_table.add_global_secondary_index(
            index_name="UserIdIndex",
            partition_key=dynamodb.Attribute(
                name="userId",
                type=dynamodb.AttributeType.STRING
            )
        )