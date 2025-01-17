import logging
from fastapi import FastAPI, HTTPException
from google.api_core.exceptions import GoogleAPIError
from src.models import ReviewResponse, ReviewRequest
from src.utils import get_files_contents, GitHubApiError, AiModel
from utils import RedisCache

log = logging.getLogger('uvicorn.error')

app = FastAPI()


@app.post("/review", response_model=ReviewResponse)
async def review_code(request: ReviewRequest):
    try:
        ReviewRequest.model_validate(request)

        files_contents: dict = await get_files_contents(request.github_repo_url)

        redis = RedisCache()
        ai_model: AiModel = AiModel(redis)

        review_text: str = await ai_model.get_review(assignment_description=request.assignment_description,
                                                     files_contents=files_contents,
                                                     candidate_level=request.candidate_level.value)
        log.debug(review_text)
        comments: str
        rating: str
        conclusion: str
        comments, rating, conclusion = AiModel.parse_review(review_text)

        return ReviewResponse(
            found_files=", ".join(files_contents.keys()),
            comments=comments,
            rating=rating,
            conclusion=conclusion,
        )

    except GitHubApiError as e:
        log.error(f"Error retrieving repository contents: {e}")
        raise HTTPException(status_code=404, detail="Repository not found or empty")
    except GoogleAPIError as e:
        log.error(f"AI model error: {e}", exc_info=True)
        raise HTTPException(status_code=502, detail="AI model error: Problem with external AI service")
    except AiModel.ParsingError as e:
        log.error(f"Parsing review error: {e}")
        raise HTTPException(status_code=502, detail="Parsing review error: Can't parsing AI response")
    except Exception as e:
        log.error(f"Unexpected error: {type(e).__name__}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
