from urllib.parse import urlencode
from fastapi import HTTPException
import httpx
import requests
import asyncio


delimiter = ';'

def checkDBFailure(response: dict):
    if response["result"] == "fail":
        raise HTTPException(status_code=502, detail="DB result is fail")

def makeURLRequest(query : str):
    encoded_query = urlencode({"query": query})
    return f"https://rahanaman.cien.or.kr/execute_query?{encoded_query}"

def get_review_keywords_all():
    """
    r = {"result" : [[id, k1;k2;k3], [id, k1;k2;k3]]}
    r["result"]
    :return:
    """
    query = (f"SELECT * "
             f"FROM bookReviewKeywordTable")
    url = makeURLRequest(query)

    response = requests.get(url)

    if response.status_code == 400:
        raise HTTPException(status_code=400, detail="Bad Request: Invalid name")
    result = response.json()
    checkDBFailure(result)

    review_keywords = []

    for item in result["result"]:
        book_id = item[0]
        keywords = item[1].split(delimiter)
        review_keywords.append([book_id, keywords])

    return review_keywords

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