import logging
from fastapi import FastAPI, HTTPException, Form, Request
from fastapi.staticfiles import StaticFiles
from google.api_core.exceptions import GoogleAPIError
from pydantic import ValidationError
from starlette.templating import Jinja2Templates
from src.models import ReviewResponse, ReviewRequest
from src.utils import get_files_contents, GitHubApiError, AiModel, Redis, ConfigError

log: logging.Logger = logging.getLogger('uvicorn.error')

app: FastAPI = FastAPI()

templates = Jinja2Templates(directory="src/templates")
app.mount("/static", StaticFiles(directory="src/static"), name="static")


@app.get("/")
async def review_page(request: Request):
    return templates.TemplateResponse(name='index.html', request=request)


@app.post("/web_review")
async def web_review(request: Request,
                     assignment_description=Form(),
                     github_repo_url=Form(),
                     candidate_level=Form()):
    try:
        review_request = ReviewRequest(assignment_description=assignment_description,
                                       github_repo_url=github_repo_url,
                                       candidate_level=candidate_level)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=f"Data validation error: {e}")
    try:
        review: ReviewResponse = await review_code(review_request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")
    context = {
        "found_files": review.found_files,
        "comments": review.comments,
        "rating": review.rating,
        "conclusion": review.conclusion,
        "assignment_description": review_request.assignment_description,
        "github_repo_url": review_request.github_repo_url,
    }
    return templates.TemplateResponse(name='review.html', request=request, context=context)


@app.post("/review", response_model=ReviewResponse)
async def review_code(request: ReviewRequest) -> ReviewResponse:
    try:
        ReviewRequest.model_validate(request)

        files_contents: dict = await get_files_contents(request.github_repo_url)

        redis: Redis = Redis()
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
    except ConfigError as e:
        log.error(f"Config error: {e}")
        raise HTTPException(status_code=500, detail="Server error")
    except Exception as e:
        log.error(f"Unexpected error: {type(e).__name__}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
