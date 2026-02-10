from pydantic import BaseModel, EmailStr, HttpUrl, Field
from typing import Optional, List
from uuid import UUID

class Candidate(BaseModel):
    full_name: str = Field(min_length=2)
    email: EmailStr
    github_url: Optional[HttpUrl]=None
    linkedin_url: Optional[HttpUrl]=None
    website_url: Optional[HttpUrl]=None
    years_experience: Optional[int]=None
    skills: List[str] = []
    education: List[str] = []
    certifications: List[str] = []
    projects: List[str] = []
    notes: List[str] = []

class CandidateDB(Candidate):
    id: UUID

class CandidateSearchResult(BaseModel):
    id: int
    full_name: str
    email: str
    github_url: str|None
    linkedin_url: str|None
    role: str
    score: float