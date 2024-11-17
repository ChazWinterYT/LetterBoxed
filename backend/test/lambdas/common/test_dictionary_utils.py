import pytest
from unittest.mock import MagicMock
import os
import boto3
from botocore.exceptions import ClientError
from lambdas.common.dictionary_utils import (
    get_dictionary,
    _fetch_dictionary_from_s3,
    _load_local_dictionary
)

# Mock environment variables
@pytest.fixture(autouse=True)
def mock_env_vars(mocker):
    mocker.patch.dict(
        os.environ, {
            "DICTIONARY_SOURCE": "local",
            "S3_BUCKET_NAME": "chazwinter.com",
            "DICTIONARY_BASE_S3_PATH": "LetterBoxed/Dictionaries/",
            "DEFAULT_LANGUAGE": "en",
            "LOCAL_DICTIONARY_PATH": "./dictionaries/{language}/dictionary.txt"
        }
    )

@pytest.fixture
def mock_s3_client(mocker):
    s3_client = MagicMock()
    mocker.patch("lambdas.common.dictionary_utils.s3", s3_client)
    return s3_client


# Tests for _load_local_dictionary
def test_load_local_dictionary(mocker):
    # Arrange
    mocker.patch("os.path.exists", return_value=True)
    mocker.patch("os.path.abspath", side_effect=lambda path: f"/absolute/path/{path}")
    mock_open = mocker.patch("builtins.open", mocker.mock_open(read_data="word1\nword2\nword3"))
    
    # Act
    words = _load_local_dictionary("en")
    
    # Assert
    assert words == ["word1", "word2", "word3"]
    mock_open.assert_called_once_with("/absolute/path/./dictionaries/en/dictionary.txt", "r")


def test_load_local_dictionary_file_not_found(mocker):
    # Arrange
    mocker.patch("os.path.exists", return_value=False)
    
    # Act & Assert
    with pytest.raises(ValueError, match="Dictionary for language 'en' not found at"):
        _load_local_dictionary("en")


# Tests for _fetch_dictionary_from_s3
def test_fetch_dictionary_from_s3(mock_s3_client):
    # Arrange
    os.environ["S3_BUCKET_NAME"] = "test-dictionary-bucket"
    os.environ["DICTIONARY_BASE_S3_PATH"] = "Dictionaries/"
    mock_s3_client.get_object.return_value = {"Body": MagicMock(read=lambda: b"word1\nword2\nword3")}

    # Act
    words = _fetch_dictionary_from_s3("en")

    # Assert
    assert words == ["word1", "word2", "word3"]
    mock_s3_client.get_object.assert_called_once_with(
        Bucket="test-dictionary-bucket", 
        Key="Dictionaries/en/dictionary.txt"
    )


def test_fetch_dictionary_from_s3_key_not_found(mock_s3_client):
    # Arrange
    mock_s3_client.get_object.side_effect = ClientError(
        {"Error": {"Code": "NoSuchKey", "Message": "Key not found"}}, "GetObject"
    )

    # Act & Assert
    with pytest.raises(ValueError, match="Dictionary for language 'en' not found in S3."):
        _fetch_dictionary_from_s3("en")


def test_fetch_dictionary_from_s3_other_error(mock_s3_client):
    # Arrange
    mock_s3_client.get_object.side_effect = ClientError(
        {"Error": {"Code": "InternalError", "Message": "Some other error"}}, "GetObject"
    )

    # Act & Assert
    with pytest.raises(RuntimeError, match="Failed to fetch dictionary from S3: An error occurred"):
        _fetch_dictionary_from_s3("en")


# Tests for get_dictionary
def test_get_dictionary_local(mocker):
    # Arrange
    mocker.patch("os.getenv", side_effect=lambda key, default: "local" if key == "DICTIONARY_SOURCE" else default)
    mock_load_local = mocker.patch("lambdas.common.dictionary_utils._load_local_dictionary", return_value=["word1", "word2"])
    
    # Act
    words = get_dictionary("en")
    
    # Assert
    assert words == ["word1", "word2"]
    mock_load_local.assert_called_once_with("en")


def test_get_dictionary_s3(mocker):
    # Arrange
    mocker.patch(
        "lambdas.common.dictionary_utils.DICTIONARY_SOURCE", 
        "s3"
    )
    mock_fetch_s3 = mocker.patch(
        "lambdas.common.dictionary_utils._fetch_dictionary_from_s3",
        return_value=["word1", "word2"]
    )

    # Act
    words = get_dictionary("en")

    # Assert
    assert words == ["word1", "word2"]
    mock_fetch_s3.assert_called_once_with("en")


def test_get_dictionary_default_language(mocker):
    # Arrange
    mocker.patch("os.getenv", side_effect=lambda key, default: "local" if key == "DICTIONARY_SOURCE" else default)
    mock_load_local = mocker.patch("lambdas.common.dictionary_utils._load_local_dictionary", return_value=["word1", "word2"])
    
    # Act
    words = get_dictionary()
    
    # Assert
    assert words == ["word1", "word2"]
    mock_load_local.assert_called_once_with("en")
