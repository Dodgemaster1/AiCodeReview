import json
import logging
import google.generativeai as genai
from google.generativeai.types import AsyncGenerateContentResponse
from .read_config import get_gemini_api_key
import typing_extensions as typing
from .redis import RedisCache

log: logging.Logger = logging.getLogger('uvicorn.error')


class Product(typing.TypedDict):
    comments: str
    rating: str
    conclusion: str


class AiModel:
    def __init__(self, redis: RedisCache) -> None:
        self.redis: RedisCache = redis
        api_key: str = get_gemini_api_key()
        genai.configure(api_key=api_key)
        self.model: genai.GenerativeModel = genai.GenerativeModel("gemini-1.5-flash",
                                                                  generation_config=genai.GenerationConfig(
                                                                      response_mime_type="application/json",
                                                                      response_schema=Product))

    async def get_review(self, assignment_description: str, files_contents: dict[str, str],
                         candidate_level: str) -> str:
        hashed_args: str = self.redis.hash_args(assignment_description, files_contents, candidate_level)
        cached_response: bytes | None = self.redis.get(hashed_args, prefix='get_review')
        if cached_response is not None:
            return cached_response.decode()

        prompt: str = f'''
        Evaluate a code review of a project submitted by a programmer with skills level <candidate_level> 
        for the task of <assignment_description>. Please analyze the provided project files (<file_contents>) 
        (if file empty just ignore it) and identify areas for improvement. 
        Provide a detailed critique in the format of three separate sections: 
        <comments> (specific issues and suggestions. Use html tags), 
        <rating> (assigning a score from 1 to 10 based on project quality and candidate level), and 
        <conclusion> (providing a final grade for the candidate).
        The output must be in JSON. Always answer according to schema.
        <assignment_description> - {assignment_description}
        candidate_level - {candidate_level}
        file_contents - {files_contents}
        '''
        response: AsyncGenerateContentResponse = await self.model.generate_content_async(prompt)
        response_text: str = response.text

        self.redis.set(hashed_args, response_text, time=3600, prefix='get_review')
        return response_text

    @staticmethod
    def parse_review(review_text: str) -> tuple[str, str, str]:
        try:
            review: dict = json.loads(review_text)
            comments: str = review['comments']
            rating: str = review['rating']
            conclusion: str = review['conclusion']
        except KeyError:
            raise AiModel.ParsingError("Error parsing AI response")
        return comments, rating, conclusion

    class ParsingError(Exception):
        pass
