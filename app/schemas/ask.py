from pydantic import BaseModel
from typing import List, Optional


class AskRequest(BaseModel):
    query: str

class VerseTextResponse(BaseModel):
    reference: str
    text: str

class TopicResponse(BaseModel):
    topic: str
    verses: List[VerseTextResponse]

class TopicListResponse(BaseModel):
    topics: List[str]

class EmotionResponse(BaseModel):
    emotion: str
    verses: List[VerseTextResponse]
    
class AskResponse(BaseModel):
    query: str
    topic_result: Optional[TopicResponse] = None
    emotion_result: Optional[EmotionResponse] = None