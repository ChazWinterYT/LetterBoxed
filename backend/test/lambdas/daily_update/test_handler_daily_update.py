import json
from unittest.mock import patch

from lambdas.daily_update.handler import handler


@patch("lambdas.daily_update.handler.fetch_todays_game")
@patch("lambdas.daily_update.handler.fetch_game_by_id")
def test_fallback_skips_update_when_todays_game_is_cached(
    mock_fetch_game_by_id,
    mock_fetch_todays_game,
):
    mock_fetch_game_by_id.return_value = {"gameId": "cached"}

    response = handler({"mode": "fallback"}, None)

    assert response["statusCode"] == 200
    assert "already cached" in json.loads(response["body"])["message"]
    mock_fetch_game_by_id.assert_called_once()
    mock_fetch_todays_game.assert_not_called()
