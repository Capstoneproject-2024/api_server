prompt_always_kor = """
You must answer in Korean language for your responses. You have to use only Korean.
"""

SecondLevel_Question_prompt = """
You will also get a sentence and a keyword which is the main theme of a sentence.
You are going to make 5 questions that encourage reading by using quotes from specific books as answers.
Questions should be about a keyword and should be deep, thought-provokable.
For example, if the text is "4.3 전쟁으로 인해 고통받는 사람들의 삶" and the keyword is "사람", then questions should be like these, "큰 고통 속에서도 인간의 존엄을 지키는 모습을 그린 문장 중 가장 기억에 남는 것은 무엇인가요?" or "고통스러운 상황 속에서도 서로를 위로하고 지지한 사람들의 모습을 그린 문장은 무엇인가요?".

Here’s how you should make questions:
1. you have to translate sentence and keyword to English.
2. Create 5 questions following the direction.
    The questions should be designed in a way that even if the reader doesn’t know the exact sentence, they can still reflect on the keyword.
    Questions shoue be possible to answer in quotes form.
        

This is precaution what you should be careful for:
- Just tell me the Questions, no small talk.

Here is the text and keyword.
text : {{text}}
keyword : {{keword}}
"""
# TODO 예시 더 집어넣기 (예시 냅다 10개 넣어보자)
SecondLevel_Question_prompt_ver2 = """
You will get a sentence and a keyword which is the main theme of a sentence.
You are going to make 5 questions that encourage reading by using quotes from specific books as answers.
Questions should be about a keyword and should be deep, thought-provokable.

For guidance, refer to the examples below.

text : 4.3 전쟁으로 인해 고통받는 사람들의 삶
keyword : 사람
- 큰 고통 속에서도 인간의 존엄을 지키는 모습을 그린 문장 중 가장 기억에 남는 것은 무엇인가요?
- 인간이란 무엇인지, 인간다움이란 무엇인지 깊이 느끼게 해 준 문장은 무엇인가요?
- 고통스러운 상황 속에서도 서로를 위로하고 지지한 사람들의 모습을 그린 문장은 무엇인가요?
- 인간이라는 존재가 가진 근원적인 약함과 동시에 위대함을 표현한 문장은 무엇인가요?
- 인간의 본질과 존재의 의미를 다시 생각하게 만든 문장은 무엇인가요?

text : 디지털 시대의 독서 문제 
keyword : 독서
- 빠르게 흘러가는 정보 속에서도 독서를 통해 얻는 깊이 있는 지혜를 표현한 문장은 어떤 것인가요?
- 독서가 우리에게 삶의 깊이를 더해준다고 느끼게 한 문장은 무엇인가요?
- 디지털 시대에 독서가 왜 여전히 중요한지, 그 본질적인 이유를 깨닫게 해 준 문장은 무엇인가요?
- 독서가 우리에게 진정한 자유나 위안을 주는 순간을 표현한 문장은 무엇인가요?
- 한 문장으로 독서의 본질을 잘 표현한 구절이 있다면, 그것은 무엇인가요?

text : 사소한 것들로 하는 사랑이었다
keyword : 사랑
- 사소한 순간들 속에서 사랑이 어떻게 드러나는지 표현한 문장은 어떤 것인가요?
- 작은 일상 속에서 사랑의 소중함을 느끼게 해 주는 문장은 무엇인가요?
- 사랑의 진정한 의미를 느끼게 해 준 문장은 무엇인가요?
- 일상 속 작은 행동들이 한 사람의 삶에 깊은 의미를 더해주는 사랑을 보여준 문장은 어떤 것인가요?
- 사랑이란 것이 말이나 행동 너머로 존재함을 느끼게 해 준 문장은 무엇인가요?

text : 청소년 스마트폰 사용 규제
keyword : 청소년
- 청소년 시기에 가장 중요한 가치나 경험이 무엇인지 생각하게 해 준 문장은 무엇인가요?
- 청소년 시기의 호기심과 성장이 어떻게 그들의 미래를 형성해 나가는지 느끼게 한 문장은 무엇인가요?
- 스마트폰과 같은 기술이 청소년들에게 긍정적 또는 부정적 영향을 미친다고 느끼게 한 문장은 무엇인가요?
- 청소년들에게 필요한 규제란 무엇인지, 그 본질에 대해 고민하게 한 문장은 무엇인가요?
- 청소년 시기에 규제가 필요하다고 느끼게 한 순간이나 이유를 표현한 문장은 무엇인가요?

text : 인생에 더 기대할 게 없다는 생각이 든다면
keyword : 인생
- 인생이란 무엇이며, 그 의미를 다시금 생각하게 해 준 문장은 무엇인가요?
- 인생에서 가장 소중한 순간이나 가치를 일깨워 준 문장은 어떤 것인가요?
- 인생의 시작과 끝을 바라보며 삶을 성찰하게 만든 문장은 무엇인가요?
- 인생이란 단순한 시간이 아닌 특별한 순간들의 축적이라고 느끼게 한 문장은 무엇인가요?
- 인생이란 여정을 어떻게 받아들이고 살아가야 할지 고민하게 한 문장은 무엇인가요?


Here’s how you should make questions:
1. you have to translate sentence and keyword to English.
2. Create 5 questions following the direction.
    The questions should be designed in a way that even if the reader doesn’t know the exact sentence, they can still reflect on the keyword.
    Questions shoue be possible to answer in quotes form.
        

This is precaution what you should be careful for:
- Just tell me the Questions, no small talk.
- Focus on keywords. It is more better that question is not about the text as long as it is about keyword and it causes deep, thought-provokable.

Here is the text and keyword.
text : {{text}}
keyword : {{keword}}
"""

SecondLevel_Question_prompt_with3Text = """
You will get sentences and a keyword which is the main theme of sentences.
Keyword is the subject of these sentences.
You are going to make 5 questions that encourage reading by using quotes from specific books as answers.
Questions should be about a keyword and should be deep, thought-provokable.
For example, if sentences are "4.3 전쟁으로 인해 고통받는 사람들의 삶,사회문제와 인간 존재의 의미, 폭력과 인간 존재의 질문" and the keyword is "사람", then questions should be like these, "큰 고통 속에서도 인간의 존엄을 지키는 모습을 그린 문장 중 가장 기억에 남는 것은 무엇인가요?" or "인간의 폭력으로 생긴 사회문제를 묘사한 문장 중 가장 기억에 남는 것은 무엇인가요?".

Here’s how you should make questions:
1. you have to translate sentences and keyword to English.
2. Create 5 questions following the direction.
    The questions should be designed in a way that even if the reader doesn’t know the exact sentence, they can still reflect on the keyword.
    Questions shoue be possible to answer in quotes form.
    
        
This is precaution what you should be careful for:
- Just tell me the Questions, no small talk.
- Focus on the keyword. The questions should be designed in a way that makes no problem to answer without knowing the sentences.
- 

Here is the sentences and keyword.
sentences : {{text}}
keyword : {{keword}}
"""
