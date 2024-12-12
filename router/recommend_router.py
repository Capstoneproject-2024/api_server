from fastapi import APIRouter, HTTPException, Depends, status
from models import *
from MySQLConnection import MySQLConnection, get_mysql_connection
from collections import defaultdict

router = APIRouter(prefix="/getRecommend")


@router.get("/question_recommend")
def get_question_recommend(
    questionID: int, db: MySQLConnection = Depends(get_mysql_connection)
):
    db.start_transaction()
    try:
        db.execute(
            f"""
SELECT 
    qrb.userID ,
    b.*,
    u.nickname AS nickname
FROM bookTable b
JOIN questionRecommendBookTable qrb ON b.id = qrb.bookID
JOIN userTable u ON qrb.userID = u.ID
WHERE qrb.questionID = {questionID};
"""
        )
        dbResult = db.fetchall()
        db.commit()

        recommends = defaultdict(list)

        for book in dbResult:
            recommends[book[0]].append(
                BookWithNickname(
                    id=book[1],
                    name=book[2],
                    author=book[3],
                    publisher=book[4],
                    year=book[5],
                    desc=book[6],
                    image=book[7],
                    ISBN=book[8],
                    nickname=book[9],
                )
            )

        return recommends

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
