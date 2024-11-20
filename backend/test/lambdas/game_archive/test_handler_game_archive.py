import json
import pytest
from unittest.mock import MagicMock
from botocore.exceptions import ClientError
from lambdas.game_archive.handler import handler  


@pytest.fixture
def mock_dynamodb_table(mocker):
    # Mock the DynamoDB Table resource
    mock_table = MagicMock()
    # Mock the DynamoDB resource and table
    mock_dynamodb_resource = MagicMock()
    mock_dynamodb_resource.Table.return_value = mock_table
    # Patch the boto3 resource to return our mock DynamoDB resource
    mocker.patch('boto3.resource', return_value=mock_dynamodb_resource)
    return mock_table


def test_handler_no_query_params(mock_dynamodb_table):
    # Arrange
    # Mock the scan method to return a set of items
    mock_dynamodb_table.scan.return_value = {
        'Items': [
            {'gameId': '20210101', 'officialGame': True},
            {'gameId': '20210102', 'officialGame': True},
            {'gameId': '20200101', 'officialGame': True},
            {'gameId': '20190101', 'officialGame': True},
            {'gameId': '20200102', 'officialGame': False},  # Not an official game
        ]
    }

    event = {
        'queryStringParameters': None  # No query parameters
    }

    # Act
    response = handler(event, None)
    body = json.loads(response['body'])

    # Assert
    assert response['statusCode'] == 200
    assert 'nytGames' in body
    assert len(body['nytGames']) == 4  # Only official games
    assert body['message'] == 'Fetched official NYT games archive successfully.'
    assert set(body['nytGames']) == {'20210101', '20210102', '20200101', '20190101'}


def test_handler_with_year_filter(mock_dynamodb_table):
    # Arrange
    # Mock the scan method to return items filtered by year
    mock_dynamodb_table.scan.return_value = {
        'Items': [
            {'gameId': '20200101', 'officialGame': True},
            {'gameId': '20200102', 'officialGame': False},  # Not an official game
        ]
    }

    event = {
        'queryStringParameters': {'year': '2020'}
    }

    # Act
    response = handler(event, None)
    body = json.loads(response['body'])

    # Assert
    assert response['statusCode'] == 200
    assert 'nytGames' in body
    assert len(body['nytGames']) == 1  # Only official games from 2020
    assert body['message'] == 'Fetched official NYT games archive successfully.'
    assert body['nytGames'] == ['20200101']


def test_handler_scan_exception(mock_dynamodb_table):
    # Arrange
    # Mock the scan method to raise an exception
    mock_dynamodb_table.scan.side_effect = Exception('Mocked scan exception')

    event = {
        'queryStringParameters': None
    }

    # Act
    response = handler(event, None)
    body = json.loads(response['body'])

    # Assert
    assert response['statusCode'] == 500
    assert 'message' in body
    assert 'error' in body
    assert body['message'] == 'Error fetching NYT games archive'
    assert body['error'] == 'Mocked scan exception'


def test_handler_with_pagination(mock_dynamodb_table):
    # Arrange
    # Create mock responses for scan with pagination
    first_response = {
        'Items': [{'gameId': f'2020{i:04d}', 'officialGame': True} for i in range(1, 101)],
        'LastEvaluatedKey': {'gameId': '2020100'}
    }
    second_response = {
        'Items': [{'gameId': f'2020{i:04d}', 'officialGame': True} for i in range(101, 201)]
        # No LastEvaluatedKey means it's the last page
    }
    # Set side effects for successive calls to scan
    mock_dynamodb_table.scan.side_effect = [first_response, second_response]

    event = {
        'queryStringParameters': None
    }

    # Act
    response = handler(event, None)
    body = json.loads(response['body'])

    # Assert
    assert response['statusCode'] == 200
    assert len(body['nytGames']) == 200
    assert body['message'] == 'Fetched official NYT games archive successfully.'
    # Check that the game IDs are as expected
    expected_game_ids = [f'2020{i:04d}' for i in range(1, 201)]
    assert body['nytGames'] == expected_game_ids
