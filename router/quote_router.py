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
WHERE groupID = {groupID}
ORDER BY date DESC;
"""
        )
        result = db.fetchall()
        db.commit()
        return GetQuestion(
            id=result[0][0],
            groupID=result[0][1],
            vocabularyID=result[0][2],
            question=result[0][3],
            date=result[0][4],
        )
    except Exception as e:
        # 오류 발생 시 롤백
        print(f"오류 발생: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="현 인용 질문 가져오는데 실패했습니다.",
        )


@router.get("/get_past_question")
def get_past_question(
    groupID: int, db: MySQLConnection = Depends(get_mysql_connection)
):
    db.start_transaction()
    try:
        db.execute(
            f"""
SELECT *
FROM groupQuestionTable
WHERE groupID = {groupID}
ORDER BY date DESC;
"""
        )
        result = db.fetchall()
        db.commit()
        return GetQuestion(
            id=result[1][0],
            groupID=result[1][1],
            vocabularyID=result[1][2],
            question=result[1][3],
            date=result[1][4],
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
    u.nickname AS nickname,
    q.bookID,
    q.quotation,
    q.date,
    b.name,
    b.author,
    b.year,
    b.image
FROM groupQuestionQuotationTable q
JOIN bookTable b ON q.bookID = b.id
JOIN userTable u ON q.userID = u.ID
WHERE q.questionID = {questionID}
  AND (
      q.userID IN (
          SELECT f.followeeID
          FROM followerTable f
          WHERE f.followerID = {userID}
      )
      OR q.userID = {userID}
  )
ORDER BY q.date DESC;

"""
        )
        dbResult = db.fetchall()
        db.commit()
        # return dbResult
        return [
            GetQuoteAnswer(
                questionID=answer[0],
                userID=answer[1],
                nickname = answer[2],
                bookID=answer[3],
                quotation=answer[4],
                date=answer[5],
                name=answer[6],
                author=answer[7],
                year=answer[8],
                image=answer[9],
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
