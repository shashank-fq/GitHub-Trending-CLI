"""
Phase 1 MVP entry point.

No CLI arguments yet (that's Phase 2) - the duration and limit are hardcoded
here just to prove the whole pipeline works end to end:
    build query -> call API -> parse JSON -> print results

Run it with:
    python -m trending.main
"""

from datetime import date, timedelta

from trending.github_api import fetch_trending_repos

# Hardcoded for now - "trending this week", top 10 results
DURATION_DAYS = 7
LIMIT = 10


def main() -> None:
    since = date.today() - timedelta(days=DURATION_DAYS)
    query = f"created:>{since.isoformat()}"

    print(f"Fetching top {LIMIT} trending repos (created after {since})...\n")

    data = fetch_trending_repos(query=query, per_page=LIMIT)
    repos = data.get("items", [])

    if not repos:
        print("No repositories found.")
        return

    for i, repo in enumerate(repos, start=1):
        name = repo["full_name"]
        stars = repo["stargazers_count"]
        print(f"{i}. {name} — ⭐ {stars:,}")


if __name__ == "__main__":
    main()
