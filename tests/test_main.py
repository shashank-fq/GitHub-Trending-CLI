import pytest
import json
from unittest.mock import Mock, patch
from datetime import date
from pathlib import Path
from trending.main import get_since_date, Repo, repo_from_api, fetch_trending_repos, GitHubAPIError

def test_get_since_date_day():
    assert get_since_date(date(2026, 8, 5), "day") == date(2026, 8, 4)

def test_get_since_date_week():
    assert get_since_date(date(2026, 8, 5), "week") == date(2026, 7, 29)

def test_get_since_date_month_boundary():
    assert get_since_date(date(2026, 3, 1), "month") == date(2026, 1, 30)

def test_get_since_date_leap_year():
    assert get_since_date(date(2024, 3, 1), "day") == date(2024, 2, 29)

def test_repo_from_api_fixture():
    fixture_path = Path("tests/fixtures/search_response.json")
    data = json.loads(fixture_path.read_text(encoding="utf-8"))

    repo = repo_from_api(data["items"][0])

    assert repo == Repo(
        name="mika50000/gpt-link",
        description="Standalone ChatGPT Session/accessToken link extractor",
        stars=38,
        language="Python",
        url="https://github.com/mika50000/gpt-link",
    )

def test_repo_from_api_handles_missing_optional_fields():
    item = {
        "full_name": "mika50000/gpt-link",
        "description": None,
        "stargazers_count": 38,
        "language": None,
        "html_url": "https://github.com/mika50000/gpt-link"
    }

    repo = repo_from_api(item)

    assert repo.description is None
    assert repo.language is None


@patch("trending.github_api.requests.get")
def test_fetch_trending_repos_returns_json(mock_get):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"items": [{"full_name": "octocat/hello-world"}]}
    mock_get.return_value = mock_response

    data = fetch_trending_repos(query="created:>2026-08-01", per_page=10)

    assert data["items"][0]["full_name"] == "octocat/hello-world"
    mock_get.assert_called_once()


@patch("trending.github_api.requests.get")
def test_fetch_trending_repos_rate_limited(mock_get):
    mock_response = Mock()
    mock_response.status_code = 403
    mock_response.headers = {
        "X-RateLimit-Remaining": "0",
        "X-RateLimit-Reset": "1780000000",
    }
    mock_get.return_value = mock_response

    with pytest.raises(GitHubAPIError) as exc_info:
        fetch_trending_repos(query="created:>2026-08-01", per_page=10)

    assert "rate limit" in str(exc_info.value).lower()


@patch("trending.github_api.requests.get")
def test_fetch_trending_repos_empty_results(mock_get):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"items": []}
    mock_get.return_value = mock_response

    data = fetch_trending_repos(query="created:>2026-08-01", per_page=10)

    assert data["items"] == []


@patch("trending.github_api.requests.get")
def test_fetch_trending_repos_malformed_json(mock_get):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.side_effect = ValueError("bad json")
    mock_get.return_value = mock_response

    with pytest.raises(GitHubAPIError) as exc_info:
        fetch_trending_repos(query="created:>2026-08-01", per_page=10)

    assert "json" in str(exc_info.value).lower()