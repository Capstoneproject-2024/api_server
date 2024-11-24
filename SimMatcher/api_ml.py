from urllib.parse import urlencode
from pydantic import BaseModel
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from RequestFormat import *
from fastapi import APIRouter, HTTPException,Depends,status
import json
from pydantic import BaseModel
from MySQLConnection import MySQLConnection, get_mysql_connection
from Extractor import *
from SimilarityMatcher import *

# Type "uvicorn [file name]:app --reload" to start server
#   -> ex) "uvicorn api_test:app --reload"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인에서 요청 허용
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

extractor = Extractor()
matcher = Matcher()

# Request Body Pydantic Models ======================================================================================

@app.post("/submit")
# For testing
async def submit_message(request: Request):
    data = await request.json()
    message = data.get("message")
    print("Received message:", message)  # 콘솔에 메시지 출력
    return {"message": f"Received: {message}"}

@app.post("/match/review2all")
async def match_similarity(request: MatchBody, db:MySQLConnection = Depends(get_mysql_connection)):
    """
    get title & review
    return matched book list (book)
    :param request:
    :return:
    """
    db.start_transaction()

    title = request.title
    review = request.review
    extracted_keywords = extractor.extract_keyword_string(review, show_similarity=False)
    book_recommend = matcher.match_both(title, extracted_keywords)
    #print(f"Title: {title}\nKeywords: {extracted_keywords}\nRecommend: {book_recommend}")

    return {"recommend": book_recommend}

@app.post("/match/quot2all")
async def match_quotation(request: QuotBody):

    title = request.title
    quot = request.quotation
    book_list = request.book_list


@app.post("/extract")
async def extract_keyword(request: Request):
    data = await request.json()
    review = data.get("review")
    keywords = extractor.extract_keyword_string(review, show_similarity=False, pos=True)
    #print(f"Received review: {review}")
    #print(f"Extracted Keywords: {keywords}")

    return {"keywords": keywords}

# DB CHECK PART =====================================================================================================

def makeURLRequest(query : str):
    # DB SQL request
    encoded_query = urlencode({"query": query})
    return f"https://rahanaman.cien.or.kr/execute_query?{encoded_query}"

def checkDBFailure(response: dict):
    if response["result"] == "fail":
        raise HTTPException(status_code=502, detail="DB result is fail")

