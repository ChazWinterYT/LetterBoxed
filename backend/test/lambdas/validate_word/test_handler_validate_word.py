import pytest
from unittest.mock import patch
from lambdas.validate_word.handler import handler
import json


def test_handler_success(mocker):
    # Arrange
    event = {
        'body': json.dumps({
            'gameId': 'game123',
            'word': 'apple',
            'sessionId': 'session1'
        })
    }

    # Mock validate_submitted_word to return a valid result
    mocker.patch('lambdas.validate_word.handler.validate_submitted_word', return_value={
        'valid': True,
        'message': 'Word accepted.',
        'game_completed': False,
        'words_used': ['APPLE']
    })

    # Act
    response = handler(event, None)

    # Assert
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['valid'] == True
    assert body['message'] == 'Word accepted.'
    assert body['words_used'] == ['APPLE']


def test_handler_missing_parameters():
    # Arrange
    event = {
        'body': json.dumps({
            'gameId': 'game123',
            'word': 'apple'
            # 'sessionId' is missing
        })
    }

    # Act
    response = handler(event, None)

    # Assert
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert 'Missing required parameters' in body['message']


def test_handler_validation_failure(mocker):
    # Arrange
    event = {
        'body': json.dumps({
            'gameId': 'game123',
            'word': 'invalidword',
            'sessionId': 'session1'
        })
    }

    # Mock validate_submitted_word to return an invalid result
    mocker.patch('lambdas.validate_word.handler.validate_submitted_word', return_value={
        'valid': False,
        'message': 'Word is not valid for this puzzle.'
    })

    # Act
    response = handler(event, None)

    # Assert
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert body['valid'] == False
    assert body['message'] == 'Word is not valid for this puzzle.'


def test_handler_exception(mocker):
    # Arrange
    event = {
        'body': json.dumps({
            'gameId': 'game123',
            'word': 'apple',
            'sessionId': 'session1'
        })
    }

    # Mock validate_submitted_word to raise an exception
    mocker.patch('lambdas.validate_word.handler.validate_submitted_word', side_effect=Exception('Test exception'))

    # Act
    response = handler(event, None)

    # Assert
    assert response['statusCode'] == 500
    body = json.loads(response['body'])
    assert body['message'] == 'An error occurred.'
