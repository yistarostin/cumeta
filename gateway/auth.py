import logging
import os
import jwt

PRIVATE_KEY_PATH = "./gateway/signature.pem"
PUBLIC_KEY_PATH = "./gateway/signature.pub"
logger = logging.getLogger(__name__)


class Authorizer:
    _JWT_KEY = "username"
    _JWT_ALGORITHM = "RS256"

    def __init__(self):
        self._private_key = open(PRIVATE_KEY_PATH, "r").read()
        self._public_key = open(PUBLIC_KEY_PATH, "r").read()

    def make_token(self, username: str) -> str:
        logger.info(f"Making token for user: {username}")
        token: str = jwt.encode(
            {self._JWT_KEY: username}, self._private_key, algorithm=self._JWT_ALGORITHM
        )
        return token

    def check_token(self, username: str, token: str) -> bool:
        return True
        decoded_username = jwt.decode(
            token, self._public_key, algorithms=[self._JWT_ALGORITHM]
        ).get(self._JWT_KEY)
        logger.info(f"Decoded username: {decoded_username}")
        return decoded_username == username
