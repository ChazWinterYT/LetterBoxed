import pytest
from unittest.mock import MagicMock
import os
from botocore.exceptions import ClientError
from lambdas.common.dictionary_utils import (
    get_dictionary,
    get_basic_dictionary,
    _fetch_dictionary_from_s3,
    _load_local_dictionary,
)

# Mock environment variables
@pytest.fixture(autouse=True)
def mock_env_vars(mocker):
    mocker.patch.dict(os.environ, {
        "DICTIONARY_SOURCE": "local",
        "S3_BUCKET_NAME": "chazwinter.com",
        "DICTIONARY_BASE_S3_PATH": "LetterBoxed/Dictionaries/",
        "DEFAULT_LANGUAGE": "en",
    }, clear=True)


@pytest.fixture
def mock_s3_client(mocker):
    s3_client = MagicMock()
    mocker.patch("lambdas.common.dictionary_utils.s3", s3_client)
    return s3_client


# Tests for _load_local_dictionary
def test_load_local_dictionary(mocker):
    mocker.patch("os.path.exists", return_value=True)
    mock_open = mocker.patch("builtins.open", mocker.mock_open(read_data="word1\nword2\nword3"))
    script_dir = os.path.dirname(os.path.abspath(_load_local_dictionary.__code__.co_filename))
    expected_dictionary_path = os.path.normpath(
        os.path.join(script_dir, '..', '..', 'dictionaries', 'en', 'dictionary.txt')
    )
    words = _load_local_dictionary("en", "dictionary")
    assert words == ["WORD1", "WORD2", "WORD3"]
    mock_open.assert_called_once_with(expected_dictionary_path, "r")


def test_load_local_dictionary_file_not_found(mocker):
    mocker.patch("os.path.exists", return_value=False)
    with pytest.raises(ValueError, match=r"Dictionary 'dictionary' for language 'en' not found at"):
        _load_local_dictionary("en", "dictionary")


def test_fetch_dictionary_from_s3(mock_s3_client):
    mock_s3_client.get_object.return_value = {"Body": MagicMock(read=lambda: b"word1\nword2\nword3")}
    words = _fetch_dictionary_from_s3("en", "dictionary")
    assert words == ["word1", "word2", "word3"]
    mock_s3_client.get_object.assert_called_once_with(
        Bucket="chazwinter.com", 
        Key="LetterBoxed/Dictionaries/en/dictionary.txt"
    )


@pytest.mark.parametrize("language", ["en", "es", "fr"])
def test_fetch_dictionary_from_s3_key_not_found(mock_s3_client, language):
    mock_s3_client.get_object.side_effect = ClientError(
        {"Error": {"Code": "NoSuchKey", "Message": "Key not found"}}, "GetObject"
    )
    with pytest.raises(ValueError, match=f"Dictionary 'dictionary.txt' for language '{language}' not found in S3."):
        _fetch_dictionary_from_s3(language, "dictionary")


def test_get_dictionary_local(mocker):
    mock_load_local = mocker.patch("lambdas.common.dictionary_utils._load_local_dictionary", return_value=["word1", "word2"])
    words = get_dictionary("en")
    assert words == ["word1", "word2"]
    mock_load_local.assert_called_once_with("en", "dictionary")


def test_get_basic_dictionary_local(mocker):
    mock_load_local = mocker.patch("lambdas.common.dictionary_utils._load_local_dictionary", return_value=["basic1", "basic2"])
    words = get_basic_dictionary("en")
    assert words == ["basic1", "basic2"]
    mock_load_local.assert_called_once_with("en", "basic")
