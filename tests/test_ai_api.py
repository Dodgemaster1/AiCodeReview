import pytest
from src.utils import AiModel


@pytest.fixture
def ai_model():
    model = AiModel()
    return model


@pytest.mark.asyncio
async def test_ai_model(ai_model):
    assignment_description = "Write hello world"
    files_contents = {"main.py": "print('Hello, World!')"}
    candidate_level = "Junior"
    review = await ai_model.get_review(assignment_description=assignment_description,
                                       files_contents=files_contents,
                                       candidate_level=candidate_level)
    assert isinstance(review, str)
    review2 = await ai_model.get_review(assignment_description, files_contents, candidate_level)
    assert review == review2


    review3 = await ai_model.get_review(assignment_description, files_contents, "Senior")
    assert review != review3

    comments, rating, conclusion = AiModel.parse_review(review)
    assert isinstance(comments, str)
    assert isinstance(rating, str)
    assert isinstance(conclusion, str)
