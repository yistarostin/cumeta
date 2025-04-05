import grpc
import datetime
from proto import posts_pb2
from proto import posts_pb2_grpc
import ormar
from google.protobuf.empty_pb2 import Empty
from db import database, Post
import logging
import sys

root = logging.getLogger()
root.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
root.addHandler(handler)
logger = logging.getLogger(__name__)


class PostService(posts_pb2_grpc.PostServiceServicer):

    async def CreatePost(self, request, context):
        logger.info("Handling creating post with request: %s", request)
        post, _ = await Post.objects.get_or_create(
            user_owner=request.creator_id,
            title=request.title,
            description=request.description,
            is_private=request.is_private,
            tags=";".join(request.tags),
            created=datetime.datetime.now(),
            updated=datetime.datetime.now(),
        )
        logger.info("Post created: %s", post)
        logger.info("Post ID: %s", post.id)
        return posts_pb2.CreatePostResponse(post_id=str(post.id))

    async def GetPost(self, request, context):
        try:
            post = await Post.objects.get(id=int(request.post_id))
            return posts_pb2.GetPostResponse(
                post=posts_pb2.Post(
                    post_id=str(post.id),
                    title=post.title,
                    description=post.description,
                    creator_id=post.user_owner,
                    created_at=str(post.created),
                    updated_at=str(post.updated),
                    is_private=post.is_private,
                    tags=post.tags.split(";"),
                )
            )
        except ormar.exceptions.NoMatch:
            context.set_details("Post not found")
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return google.protobuf.empty_pb2.Empty()

    async def UpdatePost(self, request, context):
        if not Post.objects.filter(id=int(request.post_id)).exists():
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return posts_pb2.UpdatePostRequest()
        await Post.objects.filter(id=int(request.post_id)).update(
            title=request.title,
            description=request.description,
            is_private=request.is_private,
            tags=";".join(request.tags),
            updated=datetime.datetime.now(),
        )
        # form response
        return posts_pb2.UpdatePostResponse(
            post=posts_pb2.Post(
                post_id=request.post_id,
                title=request.title,
                description=request.description,
                is_private=request.is_private,
                tags=request.tags,
            )
        )

    async def GetPosts(self, request, context):
        page = request.page
        page_size = request.page_size
        result = []
        for post_id in range(page, page + page_size):
            try:
                post = await Post.objects.get(id=post_id)
                result.append(
                    posts_pb2.Post(
                        post_id=str(post.id),
                        title=post.title,
                        description=post.description,
                        creator_id=post.user_owner,
                        created_at=str(post.created),
                        updated_at=str(post.updated),
                        is_private=post.is_private,
                        tags=post.tags.split(";"),
                    )
                )
            except ormar.exceptions.NoMatch:
                continue
        return posts_pb2.GetPostsResponse(posts=result)

    async def DeletePost(self, request, context):
        post_id = request.post_id
        try:
            post = await Post.objects.get(id=int(post_id))
            await post.delete()
            return Empty()
        except ormar.exceptions.NoMatch:
            context.set_details("Post not found")
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return Empty()
