from pydantic import BaseModel
from datetime import datetime

class ExtractBody(BaseModel):
    review: str

class MatchBody(BaseModel):
    title: str
    review: str

class QuotBody(BaseModel):
    #TODO - list name? or id?
    title: str
    quotation: str
    book_list: list[str]