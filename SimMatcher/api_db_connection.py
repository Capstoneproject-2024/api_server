from urllib.parse import urlencode
from fastapi import APIRouter, HTTPException,Depends,status
import httpx
import requests
import asyncio
from MySQLConnection import MySQLConnection, get_mysql_connection

delimiter = ';'

def checkDBFailure(response: dict):
    if response["result"] == "fail":
        raise HTTPException(status_code=502, detail="DB result is fail")

def makeURLRequest(query : str):
    encoded_query = urlencode({"query": query})
    return f"https://rahanaman.cien.or.kr/execute_query?{encoded_query}"

#================================== actual connection to DB ======================================

def get_review_keywords_all(db:MySQLConnection = Depends(get_mysql_connection)):
    """
    r = {"result" : [[id, k1;k2;k3], [id, k1;k2;k3]]}
    r["result"]
    :return:
    """
    db.start_transaction()
    try:
        db.execute(f"SELECT * FROM bookReviewKeywordTable")
        response = db.fetchall()
        db.commit()

        temp_list = []
        for book_id, keyword_list in response[0]:
            temp_list.append([book_id, keyword_list])

        return temp_list

    except Exception as e:
        # 오류 발생 시 롤백
        print(f"오류 발생: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="사용자 생성에 실패했습니다."
        )


def get_book_keywords_all():
    query = (f"SELECT * "
             f"FROM bookKeywordTable")
    url = makeURLRequest(query)

    response = requests.get(url)

    if response.status_code == 400:
        raise HTTPException(status_code=400, detail="Bad Request: Invalid name")
    result = response.json()
    checkDBFailure(result)

    book_keywords = []

    for item in result["result"]:
        book_id = item[0]
        keywords = item[1].split(delimiter)
        book_keywords.append([book_id, keywords])

    return book_keywords

"""
async def main():
    keywords = await get_book_keywords_all()
    for key in keywords:
        print(key)

asyncio.run(main())
"""


