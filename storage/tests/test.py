from unittest.mock import MagicMock, AsyncMock, patch
import pytest
from google.protobuf.empty_pb2 import Empty
import grpc
import ormar
from proto import posts_pb2
from client import PostService
from ormar.exceptions import NoMatch


@pytest.fixture
def post_service():
    """Fixture to create a PostService instance."""
    return PostService()


@pytest.fixture
def mock_context():
    """Mock gRPC context."""
    context = MagicMock()
    context.set_code = MagicMock()
    context.set_details = MagicMock()
    return context


@pytest.mark.asyncio
async def test_create_post_success(post_service, mock_context):
    mock_post = MagicMock()
    mock_post.id = 1
    with patch(
        "ormar.Model.objects.get_or_create",
        new=AsyncMock(return_value=(mock_post, True)),
    ):
        request = posts_pb2.CreatePostRequest(
            creator_id=123,
            title="New Post",
            description="Post Description",
            is_private=False,
            tags=["tag1", "tag2"],
        )
        response = await post_service.CreatePost(request, mock_context)

        assert isinstance(response, posts_pb2.CreatePostResponse)
        assert response.post_id == "1"
        mock_context.set_details.assert_not_called()
        mock_context.set_code.assert_not_called()


@pytest.mark.asyncio
async def test_update_post_success(post_service, mock_context):
    with patch("ormar.Model.objects.filter", new=MagicMock()) as mock_filter:
        mock_filter.return_value.exists = AsyncMock(return_value=True)
        mock_filter.return_value.update = AsyncMock()

        request = posts_pb2.UpdatePostRequest(
            post_id="1",
            title="Updated Title",
            description="Updated Description",
            is_private=True,
            tags=["tag1", "tag3"],
        )
        response = await post_service.UpdatePost(request, mock_context)

        assert isinstance(response, posts_pb2.UpdatePostResponse)
        assert response.post.title == "Updated Title"
        assert response.post.description == "Updated Description"
        assert response.post.is_private is True
        assert response.post.tags == ["tag1", "tag3"]
        mock_context.set_details.assert_not_called()
        mock_context.set_code.assert_not_called()


@pytest.mark.asyncio
async def test_update_post_not_found(post_service, mock_context):
    with patch("ormar.Model.objects.filter", new=MagicMock()) as mock_filter:
        mock_filter.return_value.exists = AsyncMock(return_value=False)

        request = posts_pb2.UpdatePostRequest(post_id="999")
        response = await post_service.UpdatePost(request, mock_context)

        assert isinstance(response, posts_pb2.UpdatePostRequest)
        mock_context.set_code.assert_called_once_with(grpc.StatusCode.NOT_FOUND)


@pytest.mark.asyncio
async def test_get_posts_success(post_service, mock_context):
    mock_post = MagicMock()
    mock_post.id = 1
    mock_post.title = "Test Title"
    mock_post.description = "Test Description"
    mock_post.user_owner = 123
    mock_post.created = "2023-01-01"
    mock_post.updated = "2023-01-02"
    mock_post.is_private = False
    mock_post.tags = "tag1;tag2"

    with patch("ormar.Model.objects.get", new=AsyncMock(return_value=mock_post)):
        request = posts_pb2.GetPostsRequest(page=1, page_size=2)
        response = await post_service.GetPosts(request, mock_context)

        assert isinstance(response, posts_pb2.GetPostsResponse)
        assert len(response.posts) == 2
        assert response.posts[0].post_id == "1"
        assert response.posts[0].title == "Test Title"
        mock_context.set_details.assert_not_called()
        mock_context.set_code.assert_not_called()


@pytest.mark.asyncio
async def test_delete_post_success(post_service, mock_context):
    mock_post = MagicMock()
    mock_post.delete = AsyncMock()
    with patch("ormar.Model.objects.get", new=AsyncMock(return_value=mock_post)):
        request = posts_pb2.DeletePostRequest(post_id="1")
        response = await post_service.DeletePost(request, mock_context)

        assert isinstance(response, Empty)
        mock_post.delete.assert_called_once()
        mock_context.set_details.assert_not_called()
        mock_context.set_code.assert_not_called()


@pytest.mark.asyncio
async def test_delete_post_not_found(post_service, mock_context):
    with patch(
        "ormar.Model.objects.get", new=AsyncMock(side_effect=ormar.exceptions.NoMatch)
    ):
        request = posts_pb2.DeletePostRequest(post_id="999")
        response = await post_service.DeletePost(request, mock_context)

        assert isinstance(response, Empty)
        mock_context.set_details.assert_called_once_with("Post not found")
        mock_context.set_code.assert_called_once_with(grpc.StatusCode.NOT_FOUND)
