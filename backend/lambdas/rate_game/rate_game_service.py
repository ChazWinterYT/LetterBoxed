from typing import Dict, Any
from lambdas.common.db_utils import update_game_in_db
from lambdas.common.game_schema import update_game_schema


def rate_game(game: Dict[str, Any], stars: int) -> bool:
    """
    Rates a game by incrementing the total stars and total ratings.

    Args:
        game (Dict[str, Any]): The game object to rate.
        stars (int): The number of stars to add.

    Returns:
        bool: True if the operation was successful, False otherwise.
    """
    try:
        # Calculate the new totals for totalStars and totalRatings
        total_ratings = game.get("totalRatings", 0) + 1
        total_stars = game.get("totalStars", 0) + stars
        
        # Update the game schema with the rating fields
        print(f"Updating game: {game.get('gameId')}, totalRatings: {total_ratings}, totalStars: {total_stars}")
        updated_game = update_game_schema(
            game,
            updates={
                "totalRatings": total_ratings,
                "totalStars": total_stars    
            },
        )
        
        # Pass only updated fields to the DB update utility (must also include gameId)
        update_data = {
            "gameId": updated_game["gameId"],
            "totalRatings": updated_game["totalRatings"],
            "totalStars": updated_game["totalStars"],
        }
        print(f"Updating game in DB with data: {update_data}")
        return update_game_in_db(update_data)
    except Exception as e:
        print(f"Error attempting to rate game: {str(e)}")
        return False
    