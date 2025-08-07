from pydantic import BaseModel

class StudyRequest(BaseModel):
    reference: str

class VerseResponse(BaseModel):
    verse: int
    text: str

class RelatedVerseResponse(BaseModel):
    reference: str
    text: str

class StudyResponse(BaseModel):
    reference: str
    verses: list[VerseResponse]
    related_verses: list[RelatedVerseResponse]
    #question: list[str]
