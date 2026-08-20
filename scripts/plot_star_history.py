"""
Generate a hand-drawn-style star-history chart for the project's GitHub repo.

Fetches real stargazer timestamps from the GitHub API and renders them with
matplotlib's xkcd sketch style, so the README can show organic growth instead
of a generic stock chart. Run manually:

    python3 scripts/plot_star_history.py

or let .github/workflows/star-history.yml refresh it periodically. Set
GITHUB_TOKEN to raise the API rate limit (unauthenticated requests are
capped at 60/hour).
"""

import os
import sys
from datetime import datetime

import matplotlib.pyplot as plt
import requests

REPO = "zouharvi/last-translation-benchmark"
OUT_PATH = "web/src/assets/star-history.svg"


def fetch_star_timestamps(repo: str) -> list[datetime]:
    token = os.environ.get("GITHUB_TOKEN")
    headers = {"Accept": "application/vnd.github.star+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    timestamps = []
    url = f"https://api.github.com/repos/{repo}/stargazers?per_page=100"
    while url:
        r = requests.get(url, headers=headers, timeout=30)
        r.raise_for_status()
        for entry in r.json():
            timestamps.append(datetime.strptime(entry["starred_at"], "%Y-%m-%dT%H:%M:%SZ"))
        url = r.links.get("next", {}).get("url")
    return sorted(timestamps)


def plot(repo: str, timestamps: list[datetime], out_path: str) -> None:
    counts = list(range(1, len(timestamps) + 1))

    with plt.xkcd():
        fig, ax = plt.subplots(figsize=(8, 4))
        if timestamps:
            ax.plot(timestamps, counts, linewidth=2, color="#F58231")
        ax.set_title(f"{repo} stars over time")
        ax.set_ylabel("stars")
        fig.autofmt_xdate()
        fig.tight_layout()
        fig.savefig(out_path)


if __name__ == "__main__":
    repo = sys.argv[1] if len(sys.argv) > 1 else REPO
    stars = fetch_star_timestamps(repo)
    plot(repo, stars, OUT_PATH)
    print(f"wrote {OUT_PATH} ({len(stars)} stars)")
