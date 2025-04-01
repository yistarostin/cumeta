import grpc
from concurrent import futures
import time
import datetime
from proto import posts_pb2
from proto import posts_pb2_grpc
import ormar
from db import database, Post
import logging
import sys
import asyncio
from grpc import aio

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
            return posts_pb2.GetPostResponse()

    async def UpdatePost(self, request, context):
        try:
            post = Post.get(id=request.post_id)
            if post is None:
                context.set_details("Post not found")
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return posts_pb2.Post()

            post.title = request.title
            post.description = request.description
            post.is_private = request.is_private
            post.tags.extend(request.tags)

            Post[request.post_id] = post
            return post
        if not User.objects.filter(username=user.username).exists():
            raise HTTPException(status_code=404, detail="User not found")
        await User.objects.filter(username=user.username).update(
        username=user.username,
        email=user.email,
        name=user.name,
        surname=user.surname,
        updated=datetime.datetime.now(),
        )
        return (
            content={"status": "Updated user base info for user:" + user.username},
            status_code=200,
        )

    async def DeletePost(self, request, context):
        if request.post_id in posts:
            del posts[request.post_id]
        else:
            context.set_details("Post not found")
            context.set_code(grpc.StatusCode.NOT_FOUND)
        return posts_pb2.Empty()

    async def GetPosts(self, request, context):
        post_list = list(posts.values())
        total_count = len(post_list)

        start_index = (request.page - 1) * request.page_size
        end_index = start_index + request.page_size
        paginated_posts = post_list[start_index:end_index]

        return posts_pb2.GetPostsResponse(
            total_count=total_count, posts=paginated_posts
        )


async def serve():
    if not database.is_connected:
        await database.connect()
    logging.info("Connected to a database")
    await Post.objects.get_or_create(
        user_owner="yars",
        title="test",
        description="test",
        is_private=False,
        tags=";".join(["test"]),
        created=datetime.datetime.now(),
        updated=datetime.datetime.now(),
    )
    server = aio.server()
    posts_pb2_grpc.add_PostServiceServicer_to_server(PostService(), server)
    server.add_insecure_port("0.0.0.0:50051")
    await server.start()
    logging.info("gRPC сервер запущен на порту 50051...")
    await server.wait_for_termination()
    if database.is_connected:
        await database.disconnect()


if __name__ == "__main__":
    logger.info("Attempting to start gRPC server")
    asyncio.run(serve())
    logger.info("gRPC server started")
