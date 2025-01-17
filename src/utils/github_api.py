import asyncio
import logging
from pathlib import Path
from typing import Coroutine
from httpx import Response, AsyncClient, HTTPStatusError
from pydantic import HttpUrl
from .read_config import get_github_token

log = logging.getLogger('uvicorn.error')


class GitHubApiError(Exception):
    pass


async def process_directory(client: AsyncClient, path: str = '') -> dict[str, str]:
    dir_response: Response = await client.get(path)
    dir_response.raise_for_status()
    dir_contents: dict = dir_response.json()
    repo_contents: dict[str, str] = {}
    for item in dir_contents:
        if item['type'] == 'file':
            file_name: str = str(Path(path, item['name']).as_posix()).lstrip('/')
            repo_contents[file_name] = item.get('download_url')
        elif item['type'] == 'dir':
            sub_dir_name: str = item['name']
            sub_dir_path: str = path + '/' + sub_dir_name
            sub_dir_contents: dict = await process_directory(client, sub_dir_path)
            repo_contents.update(sub_dir_contents)
    return repo_contents


async def download_file(client: AsyncClient, file_name: str, download_url: str) -> (tuple[str, str] |
                                                                                    tuple[None, None]):
    try:
        download_response: Response = await client.get(download_url)
        download_response.raise_for_status()
        content: str = download_response.content.decode(errors='ignore').replace('\x00', '')
        return file_name, content
    except HTTPStatusError as e:
        log.error(f"Error downloading {download_url}: {e}")
        return None, None
    except Exception as e:
        log.error(f"Unexpected error downloading {download_url}: {e}")
        return None, None


async def download_files(client: AsyncClient, files: dict[str, str]) -> dict[str, str]:
    download_tasks: list[Coroutine] = [download_file(client, file_name, download_url)
                                       for file_name, download_url in files.items()
                                       if download_url is not None]
    results: list = await asyncio.gather(*download_tasks)
    files_contents: dict = {file_name: data for file_name, data in results if data is not None}
    return files_contents


async def get_files_contents(repo_url: HttpUrl) -> dict[str, str]:
    token: str = get_github_token()
    headers: dict = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    try:
        repo_path_url: str = repo_url.path.removesuffix(".git")
        url: str = f"https://api.github.com/repos{repo_path_url}/contents"

        async with AsyncClient(base_url=url, headers=headers) as client:
            repo_contents: dict = await process_directory(client)
            files_contents: dict = await download_files(client, repo_contents)
            return files_contents

    except HTTPStatusError as e:
        log.error(f"Error retrieving repository contents: {e}")
        raise GitHubApiError(e)
