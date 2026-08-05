# Trending Repos

`trending-repos` is a small command-line tool that finds GitHub repositories
that are both recent and popular.

It uses the GitHub Search API to:

- filter repositories by creation date
- sort them by stars
- print a readable terminal view with name, description, stars, language, and URL

## What "trending" means here

GitHub does not provide an official public Trending API.

This tool approximates trending by searching for repositories created within a
recent time window and then sorting those repositories by star count. In other
words:

`trending = recently created + highly starred`

That is why the tool uses a query like `created:>YYYY-MM-DD` instead of reading
from `github.com/trending`.

## Install

From the project root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install .
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install .
```

After installation, run:

```bash
trending-repos
```

## Usage

Basic command:

```bash
trending-repos
```

This uses:

- `--duration week`
- `--limit 10`

Available flags:

- `--duration {day,week,month,year}`
- `--limit N`

Rules:

- `--duration` defaults to `week`
- `--limit` defaults to `10`
- `--limit` must be between `1` and `100`

## Usage Examples

Default behavior:

```bash
trending-repos
```

Top 5 repositories created in the last day:

```bash
trending-repos --duration day --limit 5
```

Top 10 repositories created in the last week:

```bash
trending-repos --duration week --limit 10
```

Top 20 repositories created in the last month:

```bash
trending-repos --duration month --limit 20
```

Top 50 repositories created in the last year:

```bash
trending-repos --duration year --limit 50
```

Smallest valid limit:

```bash
trending-repos --duration week --limit 1
```

Largest valid limit:

```bash
trending-repos --duration month --limit 100
```

## Sample Output

```text
Fetching top 10 trending repos (created after 2026-07-29)...

 1, openai/example-repo
    A clean example project showing how to build a terminal tool that searches
    recently created GitHub repositories and formats the results nicely.
    Stars: 12,483   Language: Python
    https://github.com/openai/example-repo

 2, some-org/fast-tool
    High-performance CLI for exploring interesting new repositories on GitHub.
    Stars: 8,941    Language: Go
    https://github.com/some-org/fast-tool
```

## Error Handling

The tool fails gracefully for common problems:

- invalid `--limit` values are rejected before any API call
- network failures return a clear error message
- GitHub API errors such as rate limits are reported without a Python stack trace
- empty result sets print a friendly message instead of crashing

## Development

Install runtime dependencies:

```bash
pip install -r requirements.txt
```

Run the tool without installing the command:

```bash
python -m trending.main
```

Run tests:

```bash
pytest
```

This project was inspired from https://roadmap.sh/projects/github-trending-cli
