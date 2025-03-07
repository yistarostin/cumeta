import pytest
from unittest.mock import mock_open
from auth import Authorizer
import jwt


@pytest.fixture
def authorizer(mocker):
    mocker.patch("builtins.open", mock_open(read_data="test_key"))
    return Authorizer()


def test_make_token(authorizer, mocker):
    mock_encode = mocker.patch("jwt.encode")
    mock_encode.return_value = "test_token"

    token = authorizer.make_token("test_user")

    assert token == "test_token"
    mock_encode.assert_called_once_with(
        {"username": "test_user"},
        authorizer._private_key,
        algorithm=authorizer._JWT_ALGORITHM,
    )


def test_check_token_success(authorizer, mocker):
    mock_decode = mocker.patch("jwt.decode")
    mock_decode.return_value = {"username": "test_user"}

    result = authorizer.check_token("test_user", "valid_token")

    assert result is True
    mock_decode.assert_called_once_with(
        "valid_token", authorizer._public_key, algorithms=[authorizer._JWT_ALGORITHM]
    )


def test_check_token_failure(authorizer, mocker):
    mock_decode = mocker.patch("jwt.decode")
    mock_decode.side_effect = jwt.DecodeError

    result = authorizer.check_token("test_user", "invalid_token")

    assert result is False


def test_check_token_invalid_username(authorizer, mocker):
    mock_decode = mocker.patch("jwt.decode")
    mock_decode.return_value = {"username": "another_user"}

    result = authorizer.check_token("test_user", "valid_token")

    assert result is False
