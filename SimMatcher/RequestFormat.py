from pydantic import BaseModel
from datetime import datetime

class ExtractBody(BaseModel):
    review: str

class MatchBody(BaseModel):
    title: str
    review: str
    vocab: str

class QuotBody(BaseModel):
    #TODO - list name? or id? -> id should be a integer, name should be a string
    title: str
    quotation: str
    book_list: list[str]
    vocab: str

