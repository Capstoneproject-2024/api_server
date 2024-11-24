from idlelib.query import Query
from urllib.parse import urlencode
from fastapi import APIRouter, HTTPException,Depends,status
import requests
from MySQLConnection import MySQLConnection, get_mysql_connection

delimiter = ';'

router = APIRouter(
    prefix= "/sim"
)

def checkDBFailure(response: dict):
    if response["result"] == "fail":
        raise HTTPException(status_code=502, detail="DB result is fail")

def makeURLRequest(query : str):
    encoded_query = urlencode({"query": query})
    return f"https://rahanaman.cien.or.kr/execute_query?{encoded_query}"

#================================== actual connection to DB ======================================


def get_review_keywords_all():
    """
    input: [ [book_id, "key1;key2;key3;key4;key5" ]
    output: [ [book_id, [k1, k2, ... ] ]
    :return:
    """
    db = get_mysql_connection()
    db.start_transaction()
    try:
        db.execute(f"SELECT * FROM bookKeywordTable")
        response = db.fetchall()
        db.commit()

        book_keyword_list = []

        for title, keyword_string in response:
            key = [item.strip() for item in keyword_string.split(';')]
            book_keyword = [title, key]
            book_keyword_list.append(book_keyword)

        db.close()
        return book_keyword_list

    except Exception as e:
        # 오류 발생 시 롤백
        print(f"오류 발생: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="get_review_keywords_all 오류 발생."
        )

def get_book_keywords_all():
    db = get_mysql_connection()
    db.start_transaction()

    try:
        db.execute(f"SELECT * FROM reviewKeywordTable")
        response = db.fetchall()
        db.commit()

        review_keywords_list = []

        for title, keyword_string in response:
            key = [item.strip() for item in keyword_string.split(';')]
            review_keyword = [title, key]
            review_keywords_list.append(review_keyword)

        db.close()
        return review_keywords_list

    except Exception as e:
        # 오류 발생 시 롤백
        print(f"오류 발생: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="get_review_keywords_all 오류 발생."
        )

def get_group_vocab(show_id = False):
    db = get_mysql_connection()
    db.start_transaction()
    try:
        db.execute(f"SELECT * FROM groupVocabularyTable")
        response = db.fetchall()
        db.commit()

        vocab_list = []

        for id, vocab in response:
            vocab_list.append(vocab)

        db.close()
        return response

    except Exception as e:
        # 오류 발생 시 롤백
        print(f"오류 발생: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="get_review_keywords_all 오류 발생."
        )

#"""
@router.get('/testdb')
def test_database(keyword: str,
                  db:MySQLConnection = Depends(get_mysql_connection)):
    db.start_transaction()
    try:
        db.execute(f"{keyword}")
        response = db.fetchall()
        db.commit()
        return response

    except Exception as e:
        # 오류 발생 시 롤백
        print(f"오류 발생: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="사용자 생성에 실패했습니다."
        )
#"""
#================================== Testing API ======================================

