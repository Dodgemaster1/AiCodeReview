from enum import Enum
from pydantic import BaseModel, HttpUrl, field_validator, Field, ValidationError


class CandidateLevel(Enum):
    JUNIOR = 'Junior'
    MIDDLE = 'Middle'
    SENIOR = 'Senior'


class ReviewRequest(BaseModel):
    assignment_description: str = Field(..., min_length=10)
    github_repo_url: HttpUrl
    candidate_level: CandidateLevel

    @field_validator('github_repo_url', mode='after')
    def validate_url(cls, value: HttpUrl):
        if value.host != 'github.com':
            raise ValueError('Only GitHub URLs are allowed')
        return value

class ReviewResponse(BaseModel):
    found_files: str
    comments: str
    rating: str
    conclusion: str
