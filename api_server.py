from fastapi import FastAPI, Request, HTTPException, status, Depends  # FastAPI import
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
from MySQLConnection import MySQLConnection, lifespan, get_mysql_connection


import router.user_router as user_router
import router.book_router as book_router
import router.friend_router as friend_router
import router.group_router as group_router
import router.review_router as review_router
import router.comment_router as comment_router
import router.quote_router as quote_router
import question.router as gpt_router
import router.recommend_router as recommend_router

app = FastAPI(lifespan=lifespan)

app.include_router(user_router.router)
app.include_router(book_router.router)
app.include_router(friend_router.router)
app.include_router(group_router.router)
app.include_router(review_router.router)
app.include_router(comment_router.router)
app.include_router(quote_router.router)
app.include_router(gpt_router.router)
app.include_router(recommend_router.router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인에서 요청 허용
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)


@app.get("/")
def main():
    # db.execute("SELECT count(*) FROM testDB.bookTable")
    # result = db.fetchall()
    return "hello"
