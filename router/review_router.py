from fastapi import APIRouter, HTTPException, Depends, status
from models import *
from MySQLConnection import MySQLConnection, get_mysql_connection

router = APIRouter(prefix="/review")


@router.post("/create_review/{visibilityLevel}")
def create_review(
    postReview: PostReview,
    visibilityLevel: str = "public",
    db: MySQLConnection = Depends(get_mysql_connection),
):
    db.start_transaction()
    try:
        db.execute(
            f"""
    INSERT INTO reviewTable(userID, bookID, rating, review, quote)
    VALUES({postReview.userID},{postReview.bookID},{postReview.rating},'{postReview.review}','{postReview.quote}');
    """
        )
        db.execute("SELECT LAST_INSERT_ID();")
        all_results = db.fetchall()
        db.commit()

        review_visibility(
            reviewVisibility=ReviewVisibility(
                reviewID=all_results[0][0], visibilityLevel=visibilityLevel
            ),
            db=db,
        )

        return {"result": "Success"}
    except Exception as e:
        # 오류 발생 시 롤백
        print(f"오류 발생: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="리뷰 생성에 실패했습니다."
        )


@router.post("/review_visibility")
def review_visibility(
    reviewVisibility: ReviewVisibility,
    db: MySQLConnection = Depends(get_mysql_connection),
):
    db.start_transaction()
    try:
        db.execute(
            f"INSERT INTO reviewVisibilityTable(reviewID, visibilityLevel) VALUES({reviewVisibility.reviewID},'{reviewVisibility.visibilityLevel}')"
        )
        db.commit()
        return {"result": "Success"}
    except Exception as e:
        # 오류 발생 시 롤백
        print(f"오류 발생: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="리뷰 생성에 실패했습니다."
        )


@router.get("/get_user_reviews")
def get_user_reviews(userID: int, db: MySQLConnection = Depends(get_mysql_connection)):
    try:
        db.execute("SELECT * FROM reviewTable WHERE userID = " + str(userID))
        dbResult = db.fetchall()
        db.commit()
        return [
            GetReview(
                ID=review[0],
                userID=review[1],
                bookID=review[2],
                rating=review[3],
                review=review[4],
                quote=review[5],
                reviewDate=review[6],
            )
            for review in dbResult
        ]
    except Exception as e:
        # 오류 발생 시 롤백
        print(f"오류 발생: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="사용자의 리뷰 리스트 얻기 요청에 실패했습니다.",
        )
