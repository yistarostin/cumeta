from main import _validate_request
import pytest


class MockPayload:
    def __init__(self, username, token):
        self.username = username
        self.token = token


def test_validate_request_success(mocker):
    # Arrange
    payload = MockPayload(username="valid_user", token="valid_token")
    mocker.patch("your_module.authorizer.check_token", return_value=True)

    # Act
    try:
        _validate_request(payload)
    except Exception:
        pytest.fail("HTTPException was raised")


def test_validate_request_unauthorized(mocker):
    # Arrange
    payload = MockPayload(username="invalid_user", token="invalid_token")
    mocker.patch("your_module.authorizer.check_token", return_value=False)

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        _validate_request(payload)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Unauthorized"
