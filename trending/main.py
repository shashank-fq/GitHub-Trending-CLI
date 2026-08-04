"""
Phase 1 MVP entry point.

No CLI arguments yet (that's Phase 2) - the duration and limit are hardcoded
here just to prove the whole pipeline works end to end:
    build query -> call API -> parse JSON -> print results

Run it with:
    python -m trending.main
"""
import argparse

from datetime import date, timedelta

from trending.github_api import fetch_trending_repos

DURATION_TO_DAYS ={
    "day": 1,
    "week": 7,
    "month": 30,
    "year": 365,
}
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch GitHub reprositories created recently, sorted by stars.")

    parser.add_argument("--duration", choices=DURATION_TO_DAYS.keys(), default="week", help = "Time window to search within.",)

    parser.add_argument("--limit", type = int, default= 10, help="Number of reprositories to show.",)

    return parser.parse_args()


def main() -> None:

    args = parse_args()
    duration_days =  DURATION_TO_DAYS[args.duration]

    since = date.today() - timedelta(days=duration_days)
    query = f"created:>{since.isoformat()}"

    print(f"Fetching top {args.limit} trending repos (created after {since})...\n")

    data = fetch_trending_repos(query=query, per_page=args.limit)
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
