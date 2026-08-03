"""
Handles all communication with the GitHub Search API.

Phase 1 scope: just get a successful request working and return raw JSON.
Error handling (rate limits, timeouts, bad status codes) gets added in Phase 4 -
don't worry about that yet, this is intentionally bare-bones.
"""

import requests

GITHUB_SEARCH_URL = "https://api.github.com/search/repositories"


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

    response = requests.get(GITHUB_SEARCH_URL, params=params, headers=headers, timeout=10)
    response.raise_for_status()  # bare-bones for now; Phase 4 makes this smarter

    return response.json()
