from fastapi import APIRouter, HTTPException, Depends, status
from models import *
from MySQLConnection import MySQLConnection, get_mysql_connection

router = APIRouter(prefix="/quote")


@router.get("/get_present_question")
def get_present_question(
    groupID: int, db: MySQLConnection = Depends(get_mysql_connection)
):
    db.start_transaction()
    try:
        db.execute(
            f"""
SELECT *
FROM groupQuestionCandidateTable
WHERE groupID = {groupID};
"""
        )
        result = db.fetchall()
        db.commit()
        return GetQuoteQuestionCandidate(
            id=result[0][0],
            groupID=result[0][1],
            vocabularyID=result[0][2],
            question=result[0][3],
        )
    except Exception as e:
        # 오류 발생 시 롤백
        print(f"오류 발생: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="그룹 멤버 가져오는데 실패했습니다.",
        )
