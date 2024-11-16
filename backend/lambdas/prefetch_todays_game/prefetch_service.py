import boto3
import json
import requests
from bs4 import BeautifulSoup
from datetime import date
from common.db_utils import fetch_game_by_id

def fetch_todays_game():
    url = "https://www.nytimes.com/puzzles/letter-boxed"
    response = requests.get(url)
    response.raise_for_status() # Raise an error for bad status codes

    soup = BeautifulSoup(response.text, 'html.parser')

    script_tag = soup.find("script", text=lambda t: t and "window.gameData" in t)
    if not script_tag:
        raise Exception("Could not find game data in the page.")
    
    # Extract game data from the JSON
    raw_game_data = script_tag.string.split("=", 1)[1].strip()
    game_data = json.loads(raw_game_data)

    todays_game = {
        "gameId": game_data["printDate"],
        "sides": game_data["sides"],
        "nytSolution": game_data["ourSolution"],
        "dictionary": game_data["dictionary"],
        "par": game_data["par"]
    }

    return todays_game


def game_exists_in_db(game_id):
    return fetch_game_by_id(game_id) is not None
