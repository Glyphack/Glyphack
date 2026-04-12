#!/usr/bin/env python3
"""Fetch merged PR counts from GitHub for projects listed in content/projects.md."""

import json
import os
import sys
import time
import tomllib
import urllib.parse
import urllib.request


def parse_projects_md(path):
    """Extract github_username and contributor repos from projects.md TOML frontmatter."""
    with open(path) as f:
        content = f.read()

    toml_str = content.split("+++")[1]
    frontmatter = tomllib.loads(toml_str)

    username = frontmatter.get("github_username")
    repos = [
        p["repo"]
        for p in frontmatter.get("projects", [])
        if p.get("role") == "contributor" and "repo" in p
    ]
    return username, repos


def fetch_merged_prs(username, repo):
    """Fetch count of merged PRs by username in repo."""
    query = f"author:{username} repo:{repo} type:pr is:merged"
    url = f"https://api.github.com/search/issues?q={urllib.parse.quote(query)}&per_page=1"

    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github.v3+json")
    req.add_header("User-Agent", "project-stats-fetcher")

    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"token {token}")

    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
            return data.get("total_count", 0)
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.reason}")
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 0


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    projects_md = os.path.join(project_root, "content", "projects.md")

    username, repos = parse_projects_md(projects_md)
    if not username:
        print("No github_username found in frontmatter")
        sys.exit(1)

    print(f"Fetching stats for {username}...")

    stats = {}
    for i, repo in enumerate(repos):
        print(f"  {repo}...", end=" ", flush=True)
        count = fetch_merged_prs(username, repo)
        stats[repo] = {"merged_prs": count}
        print(f"{count} merged PRs")
        if i < len(repos) - 1:
            time.sleep(2)

    data_dir = os.path.join(project_root, "data")
    os.makedirs(data_dir, exist_ok=True)

    output_path = os.path.join(data_dir, "projects_stats.json")
    with open(output_path, "w") as f:
        json.dump(stats, f, indent=2)

    print(f"\nWrote stats to {output_path}")


if __name__ == "__main__":
    main()
