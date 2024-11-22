import json
import requests
from typing import Any, Dict
from bs4 import BeautifulSoup
from datetime import date
from lambdas.common.db_utils import fetch_game_by_id

def fetch_todays_game() -> Dict[str, Any]:
    """
    Fetches today's game data from the New York Times Letter Boxed page.

    Returns:
        dict: A dictionary containing today's game data.

    Raises:
        Exception: If game data cannot be found or parsed from the page.
    """
    url = "https://www.nytimes.com/puzzles/letter-boxed"
    response = requests.get(url)
    response.raise_for_status() # Raise an error for bad status codes

    soup = BeautifulSoup(response.text, 'html.parser')

    script_tag = soup.find("script", string=lambda s: s and "window.gameData" in s)
    if not script_tag:
        raise Exception("Could not find game data in the page.")
    
    # Extract game data from the JSON
    raw_game_data = script_tag.string.split("=", 1)[1].strip()

    # Strip the trailing semicolon from the end of a JavaScript object
    if raw_game_data.endswith(";"):
        raw_game_data = raw_game_data[:-1]

    game_data = json.loads(raw_game_data)

    todays_game = {
        "gameId": game_data["printDate"],
        "gameLayout": game_data["sides"],
        "nytSolution": game_data["ourSolution"],
        "dictionary": game_data["dictionary"],
        "par": str(game_data["par"]),
        "createdBy": game_data.get("editor", ""),
    }

    return todays_game


def game_exists_in_db(game_id: str) -> bool:
    """
    Checks if a game with the given gameId exists in the database.

    Args:
        game_id (str): The unique identifier of the game.

    Returns:
        bool: True if the game exists, False otherwise.
    """
    return fetch_game_by_id(game_id) is not None
