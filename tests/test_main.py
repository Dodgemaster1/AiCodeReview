import pytest
from fastapi.testclient import TestClient
from itertools import product
from src.models import ReviewResponse
from src.main import app



@pytest.fixture
def client():
    return TestClient(app)


assignment_descriptions = [
    "Make a simple async TCP server",
    ""
]
github_repo_urls = [
    "https://github.com/Dodgemaster1/AsyncTCPServer",
    "https://non-github.com/Dodgemaster1/AsyncTCPServer",
    ""
]
candidate_levels = [
    "Junior",
    "Middle",
    "Senior",
    ""
]

all_combinations = [
    {"assignment_description": ad, "github_repo_url": url, "candidate_level": level}
    for ad, url, level in product(assignment_descriptions, github_repo_urls, candidate_levels)
]


@pytest.mark.parametrize("request_data", all_combinations)
def test_all_combinations(client, request_data):
    response = client.post("/review", json=request_data)
    if (not request_data["assignment_description"].strip()
            or not request_data["github_repo_url"].strip()
            or not request_data["candidate_level"].strip()):
        assert response.status_code == 422
    elif request_data["github_repo_url"] == "https://non-github.com/Dodgemaster1/AsyncTCPServer":
        assert response.status_code == 422
    else:
        assert response.status_code == 200
        ReviewResponse(**response.json())
