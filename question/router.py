import os
import random
from fastapi import APIRouter, Depends, HTTPException, Query, status
from dotenv import load_dotenv
from openai import AsyncOpenAI

from question.makeQuestion import makeQuestion
from MySQLConnection import *

router = APIRouter(prefix="/questionGPT")

load_dotenv()
GPT_API_KEY = os.environ.get("GPT_API_KEY")
OPENAI_MODEL = "gpt-4o-mini-2024-07-18"


client = AsyncOpenAI(api_key=GPT_API_KEY)


@router.post("/create_quote_question")
async def create_quote_question(
    groupID: int,
    db: MySQLConnection = Depends(get_mysql_connection),
):
    db.start_transaction()
    try:
        # 그룹 단어 얻기
        db.execute(
            f"""
WITH MemberBooks AS (
    SELECT r.bookID
    FROM groupMemberTable gm
    JOIN reviewTable r ON gm.memberID = r.userID
    WHERE gm.groupID = {groupID}
),
VocabularyFrequency AS (
    SELECT bvt.vocabulary, COUNT(*) AS frequency
    FROM MemberBooks mb
    JOIN bookVocabularyTable bvt ON mb.bookID = bvt.bookID
    GROUP BY bvt.vocabulary
)
SELECT vocabulary, frequency
FROM VocabularyFrequency
ORDER BY frequency DESC;
"""
        )
        dbResult = db.fetchall()
        db.commit()
        groupWord = dbResult[0][0]  # 가장 수가 많은 그룹 단어 채택

        # 그룹 단어에 해당하는 책 1권 뽑기---------------------------------
        db.execute(
            f"""
WITH MemberBooks AS (
        SELECT DISTINCT r.bookID
        FROM groupMemberTable gm
        JOIN reviewTable r ON gm.memberID = r.userID
        WHERE gm.groupID = {groupID}
    )
    SELECT mb.bookID
    FROM MemberBooks mb
    JOIN bookVocabularyTable bvt ON mb.bookID = bvt.bookID
    WHERE bvt.vocabulary = '{groupWord}';
"""
        )
        groupWordBookList = db.fetchall()
        db.commit()
        bookID = random.choice([item[0] for item in groupWordBookList])

        # book 키워드 채택--------------------------------------------
        db.execute(
            f"""
SELECT keyword FROM bookKeywordTable WHERE bookID = {bookID};
        """
        )
        bookKeywords = db.fetchall()
        db.commit()
        bookKeyword = random.choice(bookKeywords[0][0].split(";"))

        # groupVocabularyID 얻기--------------------------------------------
        db.execute(
            f"""
SELECT ID FROM groupVocabularyTable WHERE vocabulary = '{groupWord}';
        """
        )
        groupVocaID = db.fetchall()
        db.commit()

        # 질문 생성--------------------------------------------
        text = [
            {
                "text": bookKeyword,
                "keyword": groupWord,
            }  # text = 책 키워드, keyword = 그룹 단어
        ]
        questions = await makeQuestion(client=client, keywordList=text)

        # 질문 db에 저장--------------------------------------------
        db.execute(
            f"""
INSERT INTO groupQuestionTable (groupID, vocabularyID, question) VALUES ({groupID}, {groupVocaID[0][0]}, '{random.choice(questions)}');
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
            detail="사용자 생성에 실패했습니다.",
        )
