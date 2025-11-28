#!/usr/bin/env python3
"""
Fetch high-level stats using the GitHub API and dump JSON to data/stats.json
"""
import os
import json
from github import Github
from datetime import datetime, timezone

OWNER = os.environ.get("OWNER", "ManoharKonala")
TOKEN = os.environ.get("GITHUB_TOKEN")

OUT = os.environ.get("OUT", "data/stats.json")


def summarize_repos(gh, owner):
    stats = {"generated_at": datetime.now(timezone.utc).isoformat(), "repos": []}
    user = gh.get_user(owner)
    for repo in user.get_repos():
        # public & private that you have access to
        r = {
            "name": repo.name,
            "full_name": repo.full_name,
            "description": repo.description or "",
            "language": repo.language,
            "stargazers_count": repo.stargazers_count,
            "forks_count": repo.forks_count,
            "size": repo.size,
            "pushed_at": repo.pushed_at.isoformat() if repo.pushed_at else None,
        }
        stats["repos"].append(r)
    # sort by stars desc
    stats["repos"] = sorted(stats["repos"], key=lambda x: x.get("stargazers_count", 0), reverse=True)
    return stats


def main():
    if not TOKEN:
        raise SystemExit("GITHUB_TOKEN required in environment")
    gh = Github(TOKEN)
    stats = summarize_repos(gh, OWNER)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)
    print(f"Wrote stats to {OUT}")


if __name__ == "__main__":
    main()
