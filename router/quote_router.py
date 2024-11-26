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
FROM groupQuestionTable
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
            detail="현 인용 질문 가져오는데 실패했습니다.",
        )


@router.post("/create_quote_answer")
def create_quote_answer(
    answer: PostQuoteAnswer, db: MySQLConnection = Depends(get_mysql_connection)
):
    db.start_transaction()
    try:
        db.execute(
            f"INSERT INTO groupQuestionQuotationTable(questionID, userID, bookID, quotation) VALUES({answer.questionID},{answer.userID},{answer.bookID},'{answer.quotation}')"
        )
        db.commit()
        return {"result": "Success"}
    except Exception as e:
        # 오류 발생 시 롤백
        print(f"오류 발생: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="인용 답변 생성에 실패했습니다.",
        )


@router.get("/get_present_question_answers")
def get_present_question_answers(
    questionID: int, userID: int, db: MySQLConnection = Depends(get_mysql_connection)
):
    db.start_transaction()
    try:
        db.execute(
            f"""
SELECT 
    q.questionID,
    q.userID,
    q.bookID,
    q.quotation,
    b.name,
    b.author,
    b.year,
    b.image
FROM groupQuestionQuotationTable q
JOIN bookTable b ON q.bookID = b.id
WHERE q.questionID = {questionID}
  AND (
      q.userID IN (
          SELECT f.followeeID
          FROM followerTable f
          WHERE f.followerID = {userID}
      )
      OR q.userID = {userID}
  );

"""
        )
        dbResult = db.fetchall()
        db.commit()
        # return dbResult
        return [
            GetQuoteAnswer(
                questionID=answer[0],
                userID=answer[1],
                bookID=answer[2],
                quotation=answer[3],
                name=answer[4],
                author=answer[5],
                year=answer[6],
                image=answer[7],
            )
            for answer in dbResult
        ]
    except Exception as e:
        # 오류 발생 시 롤백
        print(f"오류 발생: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="현 인용 질문 답변들을 가져오는데 실패했습니다.",
        )
