import datetime
from proto import posts_pb2_grpc
from db import database, Post
import logging
import sys
import asyncio
from grpc import aio

from client import PostService

root = logging.getLogger()
root.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
root.addHandler(handler)
logger = logging.getLogger(__name__)


async def serve():
    if not database.is_connected:
        await database.connect()
    logging.info("Connected to a database")
    await Post.objects.get_or_create(
        user_owner="yars",
        title="test",
        description="test",
        is_private=True,
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
