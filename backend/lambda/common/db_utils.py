import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('LetterBoxedGames')

def add_game_to_db(game_id, letters, solutions):
    item = {
        'gameId': game_id,
        'letters': letters,
        'solutions': solutions,
    }
    table.put_item(Item=item)

def check_game_exists_in_db(game_id):
    response = table.get_item(
        Key={
            'game_id': game_id
        }
    )
    return response.get('Item', None)