import re
from uuid import uuid4
import 

def generate_game_id(letters, is_random=False, max_retries=3):
    """
    Generate unique game ID based on letters and game type
    """
    retries = 0
    while retries < max_retries:
        game_id = 
