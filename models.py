from typing import Literal, Optional
from pydantic import BaseModel
from datetime import datetime

# uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload


# friend 관련 모델
class FollowerRequest(BaseModel):
    senderID: int
    receiverID: int


class Follower(BaseModel):
    followerID: int  # 앱 사용하는 유저
    followeeID: int  # 친구신청 보낸 상대방


# review 관련 모델
class GetReview(BaseModel):
    id: int
    userID: int
    bookID: int
    rating: float
    review: str
    quote: str
    reviewDate: datetime


class ReviewWithBook(BaseModel):
    id: int
    userID: int
    bookID: int
    rating: float
    review: str
    quote: str
    reviewDate: datetime
    name: str
    author: str
    year: str
    desc: str
    image: str


class PostReview(BaseModel):
    userID: int
    bookID: int
    rating: float
    review: str
    quote: str


class ReviewVisibility(BaseModel):
    reviewID: int
    visibilityLevel: Optional[Literal["public", "private"]] = "public"


# Group 관련 모델
class Group(BaseModel):
    groupID: int
    groupName: str
    groupDescription: str
    role: str


# user 관련 모델
class UserInput(BaseModel):
    nickname: str
    email: str
    uid: str


class User(BaseModel):
    id: int
    nickname: str
    email: str
    uid: str


# Book 관련 모델
class Book(BaseModel):
    id: int
    name: str
    author: str
    publisher: str
    year: str
    desc: str
    image: str
    ISBN: str


class BookWihtoutDesc(BaseModel):
    id: int
    name: str
    author: str
    publisher: str
    year: str
    image: str
    ISBN: str


# comment  관련
class postComment(BaseModel):
    reviewID : int
    userID : int
    comment : str


class Comment(BaseModel):
    commentID : int
    reviewID: int
    userID: int
    comment: str
    commentDate : datetime


class GroupMember(BaseModel):
    groupID : int
    memberID : int