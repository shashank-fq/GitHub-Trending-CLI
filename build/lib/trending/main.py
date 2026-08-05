"""
Phase 1 MVP entry point.

No CLI arguments yet (that's Phase 2) - the duration and limit are hardcoded
here just to prove the whole pipeline works end to end:
    build query -> call API -> parse JSON -> print results

Run it with:
    python -m trending.main
"""

from dataclasses import dataclass
from typing import Any
import argparse
import textwrap
from datetime import date, timedelta

from trending.github_api import fetch_trending_repos, GitHubAPIError
DURATION_TO_DAYS ={
    "day": 1,
    "week": 7,
    "month": 30,
    "year": 365,
}

@dataclass
class Repo:
    name: str
    description: str | None
    stars: int
    language: str | None
    url: str
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch GitHub reprositories created recently, sorted by stars.")

    parser.add_argument("--duration", choices=DURATION_TO_DAYS.keys(), default="week", help = "Time window to search within.",)

    parser.add_argument("--limit", type = int, default= 10, help="Number of repositories to show.",)

    return parser.parse_args()

def repo_from_api(item: dict[str,Any]) -> Repo:
    return Repo(name=item["full_name"], description=item.get("description"), stars=item["stargazers_count"], language=item.get("language"), url = item["html_url"],)

def format_repo(index: int, repo: Repo) -> str:
    description = repo.description or "No description provided."
    language = repo.language or "Unknown"
    stars = f"{repo.stars:,}"

    wrapped_description = textwrap.fill(
        description,
        width=90,
        initial_indent="    ",
        subsequent_indent="    ",
    )

    return(
        f"{index:>2}, {repo.name}\n"
        f"{wrapped_description}\n"
        f"    Stars: {stars:<8} Language: {language}\n"
        f"    {repo.url}"
    )


def get_since_date(today: date, duration: str) -> date:
    duration_days = DURATION_TO_DAYS[duration]
    return today - timedelta(days=duration_days)


def main() -> None:

    args = parse_args()
    if args.limit < 1 or args.limit > 100:
        print("Error: --limit must be between 1 and 100")
        raise SystemExit(1)

    since = get_since_date(date.today(), args.duration)
    query = f"created:>{since.isoformat()}"

    print(f"Fetching top {args.limit} trending repos (created after {since})...\n")

    try:
        data = fetch_trending_repos(query=query, per_page=args.limit)
    except GitHubAPIError as exc:
        print(f"Error: {exc}")
        raise SystemExit(1)    
    items = data.get("items", [])
    repos = [repo_from_api(item) for item in items]

    if not repos:
        print("No repositories found.")
        return

    for i, repo in enumerate(repos, start=1):
        print(format_repo(i, repo))
        print()


if __name__ == "__main__":
    main()
