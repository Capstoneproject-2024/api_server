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


@router.get("/get_my_review")
def get_my_review(userID: int, db=Depends(get_mysql_connection)):
    try:
        db.execute(
            f"""
SELECT DISTINCT
    r.ID AS id,
    r.userID AS userID,
    r.bookID AS bookID,
    r.rating AS rating,
    r.review AS review,
    r.quote AS quote,
    r.reviewDate AS reviewDate,
    b.name AS name,
    b.author AS author,
    b.year AS year,
    b.description AS `desc`,
    b.image AS image
FROM reviewTable r
JOIN bookTable b ON r.bookID = b.ID
JOIN reviewVisibilityTable v ON r.ID = v.reviewID
WHERE r.userID = {userID}
ORDER BY r.reviewDate DESC;


"""
        )
        dbResult = db.fetchall()
        db.commit()
        return [
            ReviewWithBook(
                id=review[0],
                userID=review[1],
                bookID=review[2],
                rating=review[3],
                review=review[4],
                quote=review[5],
                reviewDate=review[6],
                name=review[7],
                author=review[8],
                year=review[9],
                desc=review[10],
                image=review[11],
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


@router.get("/get_timeline_reviews")
def get_timeline_reviews(
    userID: int, db: MySQLConnection = Depends(get_mysql_connection)
):
    try:
        db.execute(
            f"""
SELECT 
    r.ID AS id,
    r.userID AS userID,
    r.bookID AS bookID,
    r.rating AS rating,
    r.review AS review,
    r.quote AS quote,
    r.reviewDate AS reviewDate,
    b.name AS name,
    b.author AS author,
    b.year AS year,
    b.description AS `desc`,
    b.image AS image
FROM reviewTable r
JOIN bookTable b ON r.bookID = b.ID
JOIN reviewVisibilityTable v ON r.ID = v.reviewID
WHERE (
    r.userID = {userID}
    OR 
    (r.userID IN (
        SELECT followeeID
        FROM followerTable
        WHERE followerID = {userID}
    ) AND v.visibilityLevel = 'public')
)
ORDER BY r.reviewDate DESC;
"""
        )
        dbResult = db.fetchall()

        db.commit()
        return [
            ReviewWithBook(
                id=review[0],
                userID=review[1],
                bookID=review[2],
                rating=review[3],
                review=review[4],
                quote=review[5],
                reviewDate=review[6],
                name=review[7],
                author=review[8],
                year=review[9],
                desc=review[10],
                image=review[11],
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


@router.get("/get_group_timeline_reviews")
def get_group_timeline_reviews(
    userID: int, groupID: int, db: MySQLConnection = Depends(get_mysql_connection)
):
    try:
        db.execute(
            f"""
SELECT DISTINCT
    r.ID AS id,
    r.userID AS userID,
    u.nickname AS nickname,
    r.bookID AS bookID,
    r.rating AS rating,
    r.review AS review,
    r.quote AS quote,
    r.reviewDate AS reviewDate,
    b.name AS name,
    b.author AS author,
    b.year AS year,
    b.description AS `desc`,
    b.image AS image
FROM reviewTable r
JOIN bookTable b ON r.bookID = b.ID
JOIN userTable u ON r.userID = u.ID
JOIN reviewVisibilityTable v ON r.ID = v.reviewID
WHERE (
    (
        r.userID IN (
            SELECT memberID
            FROM groupMemberTable
            WHERE groupID = {groupID}
              AND memberID IN (
                  SELECT followeeID
                  FROM followerTable
                  WHERE followerID = {userID}
              )
        ) OR r.userID IN (
            SELECT adminID
            FROM groupTable
            WHERE groupID = {groupID}
        )
        AND v.visibilityLevel = 'public'
    )
    OR 
    (r.userID = {userID})
)
ORDER BY r.reviewDate DESC;
"""
        )
        dbResult = db.fetchall()
        db.commit()
        return [
            ReviewWithBook(
                id=review[0],
                userID=review[1],
                nickname=review[2],
                bookID=review[3],
                rating=review[4],
                review=review[5],
                quote=review[6],
                reviewDate=review[7],
                name=review[8],
                author=review[9],
                year=review[10],
                desc=review[11],
                image=review[12],
            )
            for review in dbResult
        ]
    except Exception as e:
        # 오류 발생 시 롤백
        print(f"오류 발생: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="사용자의 그룹 리뷰 리스트 얻기 요청에 실패했습니다.",
        )
