import boto3
import requests
from datetime import date

def fetch_and_store_todays_game():
    today_id = date.today().isoformat()

    # Check if today's game is already in the DB
    if game_exists_in_db(today_id):
        return {
            "message": "Today's game is already cached."
        }
    # Fetch today's game from NY Times website
    game_data = fetch_game_from_nyt()

    # Store in DB
    store_game_in_db(today_id, game_data)

    return {
        "message": "Today's game cached successfully: {today_id}"
    }
