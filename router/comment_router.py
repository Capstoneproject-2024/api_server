from fastapi import APIRouter, HTTPException, Depends, status
from models import *
from MySQLConnection import MySQLConnection, get_mysql_connection

router = APIRouter(prefix="/comment")


@router.post("/create_comment")
def create_comment(
    postComment: postComment,
    db: MySQLConnection = Depends(get_mysql_connection),
):
    db.start_transaction()
    try:
        db.execute(
            f"""
    INSERT INTO reviewCommentTable(reviewID, userID, comment)
    VALUES({postComment.reviewID},{postComment.userID},'{postComment.comment}');
    """
        )
        db.commit()

        return {"result": "Success"}
    except Exception as e:
        # 오류 발생 시 롤백
        print(f"오류 발생: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="코멘트 생성에 실패했습니다.",
        )


@router.get("/get_comments")
def get_comments(
    reviewID: int, userID: int, db: MySQLConnection = Depends(get_mysql_connection)
):
    try:
        db.execute(
            f"""
SELECT DISTINCT c.commentID, c.reviewID, c.userID, c.comment, c.commentDate
FROM reviewCommentTable c
LEFT JOIN followerTable f
ON c.userID = f.followeeID
WHERE c.reviewID = {reviewID}
  AND (c.userID = {userID} OR f.followerID = {userID});
"""
        )
        dbResult = db.fetchall()
        db.commit()
        return [
            Comment(
                commentID=comment[0],
                reviewID=comment[1],
                userID=comment[2],
                comment=comment[3],
                commentDate=comment[4],
            )
            for comment in dbResult
        ]
    except Exception as e:
        # 오류 발생 시 롤백
        print(f"오류 발생: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="코멘트 리스트 얻기에 실패했습니다.",
        )
