from fastapi import FastAPI, Request, HTTPException
from .RequestFormat import *
from .Extractor import *
from .SimilarityMatcher import *
from .api_db_connection import *

# Type "uvicorn [file name]:app --reload" to start server
#   -> ex) "uvicorn api_test:app --reload"

"""
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인에서 요청 허용
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)
"""

router = APIRouter(
    prefix="/sim"
)



extractor = Extractor()
matcher = Matcher()

# Request Body Pydantic Models ======================================================================================

@router.post("/submit")
# For testing
async def submit_message(request: Request):
    data = await request.json()
    message = data.get("message")
    print("Received message:", message)  # 콘솔에 메시지 출력
    return {"message": f"Received: {message}"}

@router.post("/match/basic")
async def match_basic(request: MatchBody):
    """
    get title & review
    return matched book list (book)
    :param request:
    :return:
    """
    title = request.title
    review = request.review
    vocab = request.vocab

    extracted_keywords = extractor.extract_keyword_string(review, show_similarity=False)
    book_recommend = matcher.match_both(title, extracted_keywords, vocab=vocab)
    #print(f"Title: {title}\nKeywords: {extracted_keywords}\nRecommend: {book_recommend}")

    return {"recommend": book_recommend}

@router.post("/match/quotation")
async def match_quotation(request: QuotBody):
    title = request.title
    quot = request.quotation
    book_list = request.book_list
    vocab = request.vocab

    quot_keyword = extractor.extract_keyword_string(quot,show_similarity=False)

    matcher.match_quot(title, quot_keyword, book_list, vocab, only_quot=False)

@router.post("/extract")
async def extract_keyword(request: ExtractBody):
    review = request.review
    keywords = extractor.extract_keyword_string(review, show_similarity=False, pos=True)
    #print(f"Received review: {review}")
    #print(f"Extracted Keywords: {keywords}")

    return {"keywords": keywords}

@router.get('/extractVocab')
async def extract_vocab(keywords_string: str):
    """
    :param keywords_string: Should be formed 'k1;k2;k3;k4;k5'
    :return: groupVocabulary
    """
    keywords_string = [key.strip() for key in keywords_string.split(';')]
    group_vocab = matcher.match_group_vocab(keywords_string)

    return{"groupVocabulary": group_vocab}


# DB CHECK PART =====================================================================================================


