from fastapi import FastAPI, Depends  # FastAPI import
from fastapi.middleware.cors import CORSMiddleware
from MySQLConnection import MySQLConnection, lifespan, get_mysql_connection



import router.user_router as user_router
import router.book_router as book_router
import router.friend_router as friend_router
import router.group_router as group_router
#import SimMatcher.api_db_connection as sim_tester
import SimMatcher.api_ml as sim_matcher

app = FastAPI(lifespan=lifespan)

app.include_router(user_router.router)
app.include_router(book_router.router)
app.include_router(friend_router.router)
app.include_router(group_router.router)
app.include_router(sim_matcher.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인에서 요청 허용
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

@app.get("/")
def main(db : MySQLConnection = Depends(get_mysql_connection)):
    db.execute("SELECT count(*) FROM testDB.bookTable")
    result = db.fetchall()
    return result[0][0]