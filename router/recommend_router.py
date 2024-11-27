from fastapi import APIRouter, HTTPException, Depends, status
from models import *
from MySQLConnection import MySQLConnection, get_mysql_connection


router = APIRouter(prefix="/getRecommend")


@router.get("/question_recommend")
def get_question_recommend(
    userID: int, questionID: int, db: MySQLConnection = Depends(get_mysql_connection)
):
    db.start_transaction()
    try:
        db.execute(
            f"""
SELECT b.*
FROM bookTable b
JOIN questionRecommendBookTable qrb
ON b.id = qrb.bookID
WHERE qrb.userID = {userID} AND qrb.questionID = {questionID};

"""
        )
        dbResult = db.fetchall()
        db.commit()
        return [
            Book(
                id=book[0],
                name=book[1],
                author=book[2],
                publisher=book[3],
                year=book[4],
                desc=book[5],
                image=book[6],
                ISBN=book[7],
            )
            for book in dbResult
        ]
    except Exception as e:
        # 오류 발생 시 롤백
        print(f"오류 발생: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="인용 도서 추천 얻기에 실패했습니다.",
        )


@router.get("/review_recommend")
def get_question_recommend(
    reviewID: int, db: MySQLConnection = Depends(get_mysql_connection)
):
    db.start_transaction()
    try:
        db.execute(
            f"""
SELECT b.*
FROM bookTable b
JOIN reviewRecommendBookTable rrb
ON b.id = rrb.recommendBookID
WHERE rrb.reviewID = {reviewID};
"""
        )
        dbResult = db.fetchall()
        db.commit()
        return [
            Book(
                id=book[0],
                name=book[1],
                author=book[2],
                publisher=book[3],
                year=book[4],
                desc=book[5],
                image=book[6],
                ISBN=book[7],
            )
            for book in dbResult
        ]
    except Exception as e:
        # 오류 발생 시 롤백
        print(f"오류 발생: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="인용 도서 추천 얻기에 실패했습니다.",
        )
