"""
Handles all communication with the GitHub Search API.

Phase 1 scope: just get a successful request working and return raw JSON.
Error handling (rate limits, timeouts, bad status codes) gets added in Phase 4 -
don't worry about that yet, this is intentionally bare-bones.
"""
from datetime import datetime
import requests

GITHUB_SEARCH_URL = "https://api.github.com/search/repositories"

class GitHubAPIError(Exception):
    pass

def format_rate_limit_reset(headers: dict) -> str | None:
    reset_value = headers.get("X-RateLimit-Reset")
    if not reset_value:
        return None

    try:
        reset_timestamp = int(reset_value)
    except ValueError:
        return None

    reset_time = datetime.fromtimestamp(reset_timestamp)
    return reset_time.strftime("%Y-%m-%d %H:%M:%S")

def fetch_trending_repos(query: str, per_page: int = 10) -> dict:
    """
    Fetch repositories from the GitHub Search API.

    NOTE: GitHub has no dedicated "trending" endpoint. We approximate it by
    searching for repos created recently, sorted by star count.

    Args:
        query: A GitHub search qualifier string, e.g. "created:>2026-07-27"
        per_page: How many results to return (max 100 per GitHub's API)

    Returns:
        The raw parsed JSON response from GitHub as a dict.
    """
    params = {
        "q": query,
        "sort": "stars",
        "order": "desc",
        "per_page": per_page,
    }
    headers = {
        "Accept": "application/vnd.github+json",
    }

    try:
        response = requests.get(GITHUB_SEARCH_URL, params=params, headers=headers, timeout=10)
    # response.raise_for_status()  # bare-bones for now; Phase 4 makes this smarter
    except requests.exceptions.Timeout :
        raise GitHubAPIError("Request timed out. Please try again.")
    except requests.exceptions.ConnectionError :
        raise GitHubAPIError("Could not connect to GitHub. Check your internet connection")
    except requests.exceptions.RequestException as exc :
            raise GitHubAPIError(f"Network error: {exc}")

    if response.status_code == 403:
        remaining = response.headers.get("X-RateLimit-Remaining")
        reset_time = format_rate_limit_reset(response.headers)

        if remaining == "0":
            message = "GitHub API rate limit exceeded."
            if reset_time:
                message += f" Limit resets at {reset_time}."
            raise GitHubAPIError(message)

        raise GitHubAPIError("GitHub returned 403 Forbidden.")  
    if response.status_code == 422:
        raise GitHubAPIError("GitHub rejected the query (422 Unprocessable Entity). Check the search parameters.") 
    if response.status_code != 200:
        raise GitHubAPIError(f"GitHub API returned HTTP {response.status_code}.")

    return response.json()
