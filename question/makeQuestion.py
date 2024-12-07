import re
from openai import AsyncOpenAI
from dotenv import load_dotenv
import os

from question.const import *
from question.utils import *

load_dotenv()

GPT_API_KEY = os.environ.get("GPT_API_KEY")
OPENAI_MODEL = "gpt-4o-mini-2024-07-18"


client = AsyncOpenAI(api_key=GPT_API_KEY)


async def makeQuestion(client, keywordList):
    questions = []
    for i in range(len(keywordList)):
        prompt = inject_variables(
            SecondLevel_Question_prompt, keywordList[i]
        )  # 기존 프롬프트 사용 시 temperature = 0.75로 변경
        response = await client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": prompt + prompt_always_kor},
            ],
            temperature=1,
            top_p=0.75,
            frequency_penalty=0.5,
            presence_penalty=1,
        )

        temp = response.model_dump()
        answer = temp["choices"][0]["message"]["content"]
        splitAnswer = answer.split("\n")
        questions = [re.sub(r"^\d+\.\s*", "", question) for question in splitAnswer]

    return questions
