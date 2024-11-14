import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('LetterBoxedGames')

def add_game_to_db(game_id, game_layout, standardized_hash, solution):
    game_item = {
        'gameId': game_id,
        'gameLayout': game_layout,
        'standardizedHash': standardized_hash,
        'solutions': solution,
    }
    table.put_item(Item=game_item)
    

def check_equivalent_game_exists_in_db(game_id):
    response = table.get_item(
        Key={
            'game_id': game_id
        }
    )
    return response.get('Item', None)