from pydantic import BaseModel
from typing import Optional

class ResourceRequest(BaseModel):
    user_id: str
    role: str
    topic: str
    level: str

class QuizGenerateRequest(BaseModel):
    role_profile: str
    topic_name: str
    difficulty: str

class QuizEvaluateRequest(BaseModel):
    role_profile: str
    topic_name: str
    difficulty: str
    user_answer: str
