import boto3
import requests
from datetime import date
from common.db_utils import check_game_exists_in_db

def fetch_and_store_todays_game():
    today_id = date.today().isoformat()

    # Check if today's game is already in the DB
    if game_exists_in_db(today_id):
        return {
            "message": "Today's game is already cached."
        }

    return {
        "message": "Today's game cached successfully: {today_id}"
    }

def game_exists_in_db(game_id):
    return check_game_exists_in_db(game_id) is not None
