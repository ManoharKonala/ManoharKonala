#!/usr/bin/env python3
"""
Auto-update script for GitHub profile README.
Fetches latest stats and regenerates dynamic content.
"""

import os
import sys
import json
import requests
from datetime import datetime
from pathlib import Path

# GitHub API setup
GITHUB_USERNAME = "ManoharKonala"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

def get_github_api_headers():
    """Get headers for GitHub API requests."""
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    return headers

def fetch_repo_stats(repo_name):
    """Fetch statistics for a specific repository."""
    url = f"https://api.github.com/repos/{repo_name}"
    headers = get_github_api_headers()
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return {
                "stars": data.get("stargazers_count", 0),
                "forks": data.get("forks_count", 0),
                "updated": data.get("updated_at", ""),
                "description": data.get("description", ""),
            }
    except Exception as e:
        print(f"Error fetching stats for {repo_name}: {e}")
    
    return {"stars": 0, "forks": 0, "updated": "", "description": ""}

def fetch_user_stats():
    """Fetch user statistics from GitHub API."""
    url = f"https://api.github.com/users/{GITHUB_USERNAME}"
    headers = get_github_api_headers()
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return {
                "followers": data.get("followers", 0),
                "following": data.get("following", 0),
                "public_repos": data.get("public_repos", 0),
            }
    except Exception as e:
        print(f"Error fetching user stats: {e}")
    
    return {"followers": 0, "following": 0, "public_repos": 0}

def update_profile_meta():
    """Update profile metadata with latest stats."""
    meta_path = Path("profile_meta.json")
    
    if not meta_path.exists():
        print("profile_meta.json not found. Skipping update.")
        return
    
    with open(meta_path, "r") as f:
        meta = json.load(f)
    
    # Update featured projects stats
    for project in meta.get("featuredProjects", []):
        repo_name = project.get("repo", "")
        if repo_name:
            stats = fetch_repo_stats(repo_name)
            project["stars"] = stats["stars"]
            if stats["description"]:
                project["description"] = stats["description"]
    
    # Update user stats
    user_stats = fetch_user_stats()
    meta["stats"] = user_stats
    meta["lastUpdated"] = datetime.now().isoformat()
    
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)
    
    print("Profile metadata updated successfully!")

def generate_contribution_image():
    """Generate or update contribution heatmap image URL."""
    # The contribution graph is already using ghchart.rshah.org
    # This function can be extended to generate a local image if needed
    pass

def main():
    """Main update function."""
    print("Starting profile README update...")
    
    # Change to repository root
    repo_root = Path(__file__).parent.parent
    os.chdir(repo_root)
    
    # Update metadata
    update_profile_meta()
    
    print("Profile update completed!")

if __name__ == "__main__":
    main()
