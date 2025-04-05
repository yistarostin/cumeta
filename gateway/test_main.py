import pytest
from unittest.mock import AsyncMock, Mock, patch
from fastapi.testclient import TestClient
from gateway.main import app
from google.protobuf.empty_pb2 import Empty
from gateway.proto import posts_pb2

client = TestClient(app)


@pytest.fixture
def mock_stub():
    with patch("gateway.main.stub") as mock_stub:
        yield mock_stub


@pytest.fixture
def mock_validate_request():
    with patch("gateway.main._validate_request") as mock_validate:
        mock_validate.return_value = True
        yield mock_validate


def test_posts_create_success(mock_stub, mock_validate_request):
    mock_stub.CreatePost = Mock(
        return_value=posts_pb2.CreatePostResponse(post_id="123")
    )

    payload = {
        "title": "Test Post",
        "description": "This is a test post",
        "creator_id": "user1",
        "is_private": False,
        "tags": ["tag1", "tag2"],
        "username": "user1",
        "token": "valid_token",
    }

    response = client.post("/posts/create", json=payload)

    assert response.status_code == 200
    assert response.json() == {"post_id": "123"}

    mock_stub.CreatePost.assert_called_once()
    grpc_request = mock_stub.CreatePost.call_args[0][0]
    assert grpc_request.title == "Test Post"
    assert grpc_request.description == "This is a test post"
    assert grpc_request.creator_id == "user1"
    assert grpc_request.is_private is False
    assert grpc_request.tags == ["tag1", "tag2"]


def test_posts_get_success(mock_stub, mock_validate_request):
    mock_stub.GetPost = Mock(
        return_value=posts_pb2.GetPostResponse(
            post=posts_pb2.Post(
                post_id="123",
                title="Test Post",
                description="This is a test post",
                creator_id="user1",
                created_at="2025-04-01T00:00:00",
                updated_at="2025-04-02T00:00:00",
                is_private=False,
                tags=["tag1", "tag2"],
            )
        )
    )

    payload = {
        "post_id": "123",
        "username": "user1",
        "token": "valid_token",
    }

    response = client.post("/posts/get", json=payload)

    assert response.status_code == 200
    assert response.json() == {
        "post_id": "123",
        "title": "Test Post",
        "description": "This is a test post",
        "creator_id": "user1",
        "created_at": "2025-04-01T00:00:00",
        "updated_at": "2025-04-02T00:00:00",
    }

    mock_stub.GetPost.assert_called_once()
    grpc_request = mock_stub.GetPost.call_args[0][0]
    assert grpc_request.post_id == "123"


def test_posts_update_success(mock_stub, mock_validate_request):
    mock_stub.UpdatePost = Mock(
        return_value=posts_pb2.UpdatePostResponse(
            post=posts_pb2.Post(
                post_id="123",
                title="Updated Post",
                description="This is an updated test post",
                creator_id="user1",
                created_at="2025-04-01T00:00:00",
                updated_at="2025-04-02T00:00:00",
            )
        )
    )

    payload = {
        "post_id": "123",
        "title": "Updated Post",
        "description": "This is an updated test post",
        "is_private": False,
        "tags": ["tag1", "tag2"],
        "username": "user1",
        "token": "valid_token",
    }

    response = client.post("/posts/update", json=payload)

    assert response.status_code == 200
    assert response.json() == {
        "post_id": "123",
        "title": "Updated Post",
        "description": "This is an updated test post",
        "creator_id": "user1",
        "created_at": "2025-04-01T00:00:00",
        "updated_at": "2025-04-02T00:00:00",
    }

    mock_stub.UpdatePost.assert_called_once()
    grpc_request = mock_stub.UpdatePost.call_args[0][0]
    assert grpc_request.post_id == "123"
    assert grpc_request.title == "Updated Post"
    assert grpc_request.description == "This is an updated test post"
    assert grpc_request.is_private is False
    assert grpc_request.tags == ["tag1", "tag2"]


def test_posts_delete_success(mock_stub, mock_validate_request):
    mock_stub.DeletePost = Mock(return_value=Empty())

    payload = {
        "post_id": "123",
        "username": "user1",
        "token": "valid_token",
    }

    response = client.post("/posts/delete", json=payload)

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "Post deleted"}

    mock_stub.DeletePost.assert_called_once()


def test_posts_get_all_success(mock_stub, mock_validate_request):
    mock_stub.GetPosts = Mock(
        return_value=posts_pb2.GetPostsResponse(
            posts=[
                posts_pb2.Post(
                    post_id="1",
                    title="Test Post",
                    description="This is a test post",
                    creator_id="user1",
                    created_at="2025-04-01T00:00:00",
                    updated_at="2025-04-02T00:00:00",
                    is_private=False,
                    tags=["tag1", "tag2"],
                ),
                posts_pb2.Post(
                    post_id="2",
                    title="Test Post",
                    description="This is a test post",
                    creator_id="user2",
                    created_at="2025-04-01T00:00:00",
                    updated_at="2025-04-02T00:00:00",
                    is_private=False,
                    tags=["tag1", "tag2"],
                ),
                posts_pb2.Post(
                    post_id="3",
                    title="Test Post",
                    description="This is a test post",
                    creator_id="user1",
                    created_at="2025-04-01T00:00:00",
                    updated_at="2025-04-02T00:00:00",
                    is_private=True,
                    tags=["tag1", "tag2"],
                ),
                posts_pb2.Post(
                    post_id="4",
                    title="Test Post",
                    description="This is a test post",
                    creator_id="user2",
                    created_at="2025-04-01T00:00:00",
                    updated_at="2025-04-02T00:00:00",
                    is_private=True,
                    tags=["tag1", "tag2"],
                ),
            ],
            total_count=4,
        )
    )

    payload = {
        "username": "user1",
        "token": "valid_token",
        "page_number": 1,
        "page_size": 4,
    }

    response = client.post("/posts/get_many", json=payload)

    assert response.status_code == 200
    assert response.json() == [
        {
            "post_id": "1",
            "title": "Test Post",
            "description": "This is a test post",
            "creator_id": "user1",
            "created_at": "2025-04-01T00:00:00",
            "updated_at": "2025-04-02T00:00:00",
            "is_private": False,
        },
        {
            "post_id": "2",
            "title": "Test Post",
            "description": "This is a test post",
            "creator_id": "user2",
            "created_at": "2025-04-01T00:00:00",
            "updated_at": "2025-04-02T00:00:00",
            "is_private": False,
        },
        {
            "post_id": "3",
            "title": "Test Post",
            "description": "This is a test post",
            "creator_id": "user1",
            "created_at": "2025-04-01T00:00:00",
            "updated_at": "2025-04-02T00:00:00",
            "is_private": True,
        },
    ]
