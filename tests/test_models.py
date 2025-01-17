import pytest
from pydantic import ValidationError

from src.models import CandidateLevel, ReviewRequest


def test_valid_github_url():
    valid_url = "https://github.com/username/repo.git"
    ReviewRequest(
        assignment_description="Some description",
        github_repo_url=valid_url,
        candidate_level=CandidateLevel.JUNIOR.value,
    )


def test_invalid_host():
    invalid_url = "https://not-github.com/username/repo.git"
    with pytest.raises(ValidationError):
        ReviewRequest(
            assignment_description="Some description",
            github_repo_url=invalid_url,
            candidate_level=CandidateLevel.JUNIOR.value,
        )


def test_invalid_candidate_level():
    valid_url = "https://github.com/username/repo.git"
    invalid_level = "Invalid"
    with pytest.raises(ValidationError):
        ReviewRequest(
            assignment_description="Some description",
            github_repo_url=valid_url,
            candidate_level=invalid_level,
        )

def test_invalid_description():
    invalid_description = "213"
    valid_url = "https://github.com/username/repo.git"
    with pytest.raises(ValidationError):
        ReviewRequest(
            assignment_description=invalid_description,
            github_repo_url=valid_url,
            candidate_level=CandidateLevel.JUNIOR.value,
        )