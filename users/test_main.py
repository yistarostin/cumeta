import pytest
from fastapi.testclient import TestClient
from users.main import app

client = TestClient(app)


@pytest.mark.asyncio
async def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)  # Expecting a list of users


@pytest.mark.asyncio
async def test_create_user():
    user_data = {"username": "test_user", "password": "secure_password"}

    response = client.post("/create/", json=user_data)
    assert response.status_code == 200
    assert response.json()["username"] == "test_user"

    response_duplicate = client.post("/create/", json=user_data)
    assert response_duplicate.status_code == 400
    assert response_duplicate.json()["detail"] == "Username already exists"


@pytest.mark.asyncio
async def test_get_user():
    response = client.get("/get/test_user")
    assert response.status_code == 200
    assert response.json()["username"] == "test_user"

    response_not_found = client.get("/get/unknown_user")
    assert response_not_found.status_code == 404
    assert response_not_found.json()["detail"] == "User not found"


@pytest.mark.asyncio
async def test_get_info_user():
    response = client.get("/get_info/test_user")
    assert response.status_code == 200
    # Check if user info is returned correctly (expand based on structure)

    response_not_found = client.get("/get_info/unknown_user")
    assert response_not_found.status_code == 404
    assert response_not_found.json()["detail"] == "User not found"


@pytest.mark.asyncio
async def test_authorize():
    login_data = {"username": "test_user", "password": "secure_password"}
    response = client.post("/authorize", json=login_data)
    assert response.status_code == 200
    assert response.json()["status"] == "Authorized"

    login_wrong = {"username": "test_user", "password": "wrong_password"}
    response_fail = client.post("/authorize", json=login_wrong)
    assert response_fail.status_code == 404


@pytest.mark.asyncio
async def test_edit_user_info():
    edit_data = {
        "username": "test_user",
        "email": "new_email@mail.com",
        "name": "New Name",
        "surname": "New Surname",
    }

    response = client.post("/edit", json=edit_data)
    assert response.status_code == 200
    assert "Updated user base info for user:" in response.json()["status"]


@pytest.mark.asyncio
async def test_edit_info():
    edit_info_data = {
        "username": "test_user",
        "about": "Updated about",
        "relationship_status": "Single",
        "education": "University",
        "phone_number": "1234567890",
        "job": "Developer",
        "birthdate": "1990-01-01",
    }

    response = client.post("/edit_info", json=edit_info_data)
    assert response.status_code == 200
    assert "Updated user info for user:" in response.json()["status"]


@pytest.mark.asyncio
async def test_startup_and_shutdown():
    # You can include tests to verify startup if needed
    pass
