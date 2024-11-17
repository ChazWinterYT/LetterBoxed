import pytest
import requests
from lambdas.prefetch_todays_game.prefetch_service import fetch_todays_game

def test_fetch_todays_game(mocker):
    mocker.patch("lambdas.prefetch_todays_game.prefetch_service.requests.get")
    # Mock a response for the requests.get call
    mock_response = mocker.Mock()
    mock_response.text = """
    <script>
        window.gameData = {
            "printDate": "2024-11-16",
            "sides": ["PRO", "CTI", "DGN", "SAH"],
            "ourSolution": ["CHINSTRAP", "PAGODA"],
            "dictionary": ["ARGH", "ACAI"],
            "par": 4
        };
    </script>
    """
    mock_response.raise_for_status = lambda: None
    requests.get.return_value = mock_response

    result = fetch_todays_game()

    assert result["gameId"] == "2024-11-16"
    assert result["gameLayout"] == ["PRO", "CTI", "DGN", "SAH"]
