import pytest
from httpx import AsyncClient
from pydantic import HttpUrl
from src.utils.github_api import get_files_contents, download_file, GitHubApiError

@pytest.mark.asyncio
async def test_download_file():
    client = AsyncClient()
    file_name = "README.md"
    download_url = "https://raw.githubusercontent.com/Dodgemaster1/AsyncTCPServer/master/README.md"

    file_name, content = await download_file(client, file_name, download_url)

    assert file_name == "README.md"
    assert content is not None

@pytest.mark.asyncio
async def test_get_files_contents():
    url = HttpUrl("https://github.com/Dodgemaster1/AsyncTCPServer")
    files_contents = await get_files_contents(url)
    assert files_contents is not None
    assert isinstance(files_contents, dict)

@pytest.mark.asyncio
async def test_wrong_url():
    url = HttpUrl("https://non-github.com/not-a-repo")
    with pytest.raises(GitHubApiError):
        await get_files_contents(url)
