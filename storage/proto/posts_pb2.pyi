from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import (
    ClassVar as _ClassVar,
    Iterable as _Iterable,
    Mapping as _Mapping,
    Optional as _Optional,
    Union as _Union,
)

DESCRIPTOR: _descriptor.FileDescriptor

class CreatePostRequest(_message.Message):
    __slots__ = ("title", "description", "creator_id", "is_private", "tags")
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    CREATOR_ID_FIELD_NUMBER: _ClassVar[int]
    IS_PRIVATE_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    title: str
    description: str
    creator_id: str
    is_private: bool
    tags: _containers.RepeatedScalarFieldContainer[str]
    def __init__(
        self,
        title: _Optional[str] = ...,
        description: _Optional[str] = ...,
        creator_id: _Optional[str] = ...,
        is_private: bool = ...,
        tags: _Optional[_Iterable[str]] = ...,
    ) -> None: ...

class DeletePostRequest(_message.Message):
    __slots__ = ("post_id",)
    POST_ID_FIELD_NUMBER: _ClassVar[int]
    post_id: str
    def __init__(self, post_id: _Optional[str] = ...) -> None: ...

class UpdatePostRequest(_message.Message):
    __slots__ = ("post_id", "title", "description", "is_private", "tags")
    POST_ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    IS_PRIVATE_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    post_id: str
    title: str
    description: str
    is_private: bool
    tags: _containers.RepeatedScalarFieldContainer[str]
    def __init__(
        self,
        post_id: _Optional[str] = ...,
        title: _Optional[str] = ...,
        description: _Optional[str] = ...,
        is_private: bool = ...,
        tags: _Optional[_Iterable[str]] = ...,
    ) -> None: ...

class GetPostRequest(_message.Message):
    __slots__ = ("post_id",)
    POST_ID_FIELD_NUMBER: _ClassVar[int]
    post_id: str
    def __init__(self, post_id: _Optional[str] = ...) -> None: ...

class GetPostsRequest(_message.Message):
    __slots__ = ("page", "page_size")
    PAGE_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    page: int
    page_size: int
    def __init__(
        self, page: _Optional[int] = ..., page_size: _Optional[int] = ...
    ) -> None: ...

class Post(_message.Message):
    __slots__ = (
        "post_id",
        "title",
        "description",
        "creator_id",
        "created_at",
        "updated_at",
        "is_private",
        "tags",
    )
    POST_ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    CREATOR_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    IS_PRIVATE_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    post_id: str
    title: str
    description: str
    creator_id: str
    created_at: str
    updated_at: str
    is_private: bool
    tags: _containers.RepeatedScalarFieldContainer[str]
    def __init__(
        self,
        post_id: _Optional[str] = ...,
        title: _Optional[str] = ...,
        description: _Optional[str] = ...,
        creator_id: _Optional[str] = ...,
        created_at: _Optional[str] = ...,
        updated_at: _Optional[str] = ...,
        is_private: bool = ...,
        tags: _Optional[_Iterable[str]] = ...,
    ) -> None: ...

class GetPostResponse(_message.Message):
    __slots__ = ("post",)
    POST_FIELD_NUMBER: _ClassVar[int]
    post: Post
    def __init__(self, post: _Optional[_Union[Post, _Mapping]] = ...) -> None: ...

class GetPostsResponse(_message.Message):
    __slots__ = ("posts", "total_count")
    POSTS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    posts: _containers.RepeatedCompositeFieldContainer[Post]
    total_count: int
    def __init__(
        self,
        posts: _Optional[_Iterable[_Union[Post, _Mapping]]] = ...,
        total_count: _Optional[int] = ...,
    ) -> None: ...

class CreatePostResponse(_message.Message):
    __slots__ = ("post_id",)
    POST_ID_FIELD_NUMBER: _ClassVar[int]
    post_id: str
    def __init__(self, post_id: _Optional[str] = ...) -> None: ...
