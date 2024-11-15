import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('LetterBoxedGames')

def add_game_to_db(game_id, game_layout, standardized_hash, two_word_solutions, three_word_solutions):
    game_item = {
        'gameId': game_id,
        'gameLayout': game_layout,
        'standardizedHash': standardized_hash,
        'twoWordSolutions': two_word_solutions,
        'threeWordSolutions': three_word_solutions
    }
    table.put_item(Item=game_item)


def fetch_solutions_by_standardized_hash(standardized_hash):
    response = table.query(
        IndexName="StandardizedHashIndex",
        KeyConditionExpression=Key("standardizedHash").eq(standardized_hash)
    )
    
    items = response.get("Items", [])
    
    # Return the first Item that contains solutions
    for item in items:
        if "twoWordSolutions" in item and "threeWordSolutions" in item:
            return {
                "twoWordSolutions": item["twoWordSolutions"],
                "threeWordSolutions": item["threeWordSolutions"]
            }
    
    # Return None if no solutions are found
    return None