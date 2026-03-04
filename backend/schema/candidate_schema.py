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
    id: UUID
    full_name: str
    email: str
    github_url: str|None
    linkedin_url: str|None
    website_url: str|None = None
    location: str|None = None
    years_experience: int|None = None
    skills: str|None = None
    role: str
    score: float


class CandidateCreateRequest(BaseModel):
    full_name: str = Field(min_length=2)
    email: EmailStr
    recent_role: str = Field(min_length=2)
    github_url: Optional[HttpUrl] = None
    linkedin_url: Optional[HttpUrl] = None
    website_url: Optional[HttpUrl] = None
    location: Optional[str] = None
    years_experience: Optional[int] = Field(default=None, ge=0)
    skills: List[str] = []
    summary: str = ""


class CandidateUpdateRequest(BaseModel):
    full_name: Optional[str] = Field(default=None, min_length=2)
    email: Optional[EmailStr] = None
    recent_role: Optional[str] = Field(default=None, min_length=2)
    github_url: Optional[HttpUrl] = None
    linkedin_url: Optional[HttpUrl] = None
    website_url: Optional[HttpUrl] = None
    location: Optional[str] = None
    years_experience: Optional[int] = Field(default=None, ge=0)
    skills: Optional[List[str]] = None
    summary: Optional[str] = None


class CandidateMutationResponse(BaseModel):
    id: UUID
    message: str
