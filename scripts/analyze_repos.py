#!/usr/bin/env python3
"""
Gather commit-by-commit language usage, commit time analysis, and repo complexity metrics.
"""
import os
import json
from datetime import datetime
from collections import defaultdict, Counter
from github import Github

OWNER = os.environ.get('OWNER', 'ManoharKonala')
TOKEN = os.environ.get('GITHUB_TOKEN')
OUT_JSON = os.environ.get('OUT_JSON', 'data/analysis.json')
OUT_MD = os.environ.get('OUT_MD', 'data/analysis.md')

EXT_LANG_MAP = {
    '.py': 'Python',
    '.ipynb': 'Jupyter Notebook',
    '.ts': 'TypeScript',
    '.js': 'JavaScript',
    '.html': 'HTML',
    '.css': 'CSS',
    '.md': 'Markdown',
    '.yml': 'YAML',
    '.yaml': 'YAML',
    '.json': 'JSON',
    '.java': 'Java',
    '.go': 'Go',
    '.rs': 'Rust',
    '.cs': 'C#',
    '.cpp': 'C++',
    '.c': 'C',
}


def ext_to_lang(ext):
    return EXT_LANG_MAP.get(ext.lower(), None)


def analyze_commits(gh, owner):
    user = gh.get_user(owner)
    repo_list = list(user.get_repos())
    analysis = {
        'generated_at': datetime.utcnow().isoformat(),
        'owner': owner,
        'repos': {}
    }

    overall_ext_counter = Counter()
    overall_commit_hours = Counter()
    overall_commit_days = Counter()
    total_commits = 0

    for repo in repo_list:
        repo_name = repo.name
        analysis['repos'][repo_name] = {'full_name': repo.full_name, 'language': repo.language, 'stars': repo.stargazers_count, 'forks': repo.forks_count, 'size': repo.size}
        # fetch commits authored by owner
        try:
            commits = repo.get_commits(author=owner)
        except Exception:
            # skip repos with restricted access
            commits = []
        repo_ext_counter = Counter()
        commit_count = 0
        # limit sample to 100 commits per repo for performance
        for i, c in enumerate(commits):
            if i >= 100:
                break
            sha = c.sha
            commit_obj = repo.get_commit(sha)
            # files changed on commit
            files = getattr(commit_obj, 'files', [])
            for f in files:
                filename = f.filename
                ext = os.path.splitext(filename)[1]
                lang = ext_to_lang(ext)
                if not lang:
                    # fallback to repo language
                    lang = repo.language if repo.language else 'Other'
                repo_ext_counter[lang] += 1
                overall_ext_counter[lang] += 1
            # commit time
            committer = commit_obj.commit.committer
            if committer and committer.date:
                dt = committer.date
                overall_commit_hours[dt.hour] += 1
                overall_commit_days[dt.strftime('%A')] += 1
            commit_count += 1
            total_commits += 1
        analysis['repos'][repo_name]['commit_sample_count'] = commit_count
        analysis['repos'][repo_name]['top_languages_by_commits'] = repo_ext_counter.most_common(3)

    analysis['summary'] = {
        'total_repos': len(repo_list),
        'total_commits_sampled': total_commits,
        'primary_languages_by_commits': overall_ext_counter.most_common(10),
        'commit_hours_distribution': dict(sorted(overall_commit_hours.items(), key=lambda x:x[0])),
        'commit_days_distribution': dict(overall_commit_days),
    }

    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2)

    # write human readable summary
    with open(OUT_MD, 'w', encoding='utf-8') as md:
        md.write(f"# Analysis Report for {owner}\n\n")
        md.write(f"Generated at: {analysis['generated_at']} UTC\n\n")
        md.write(f"Total repos scanned: {analysis['summary']['total_repos']}\n\n")
        md.write("## Primary languages by commits (sampled)\n\n")
        for lang, cnt in analysis['summary']['primary_languages_by_commits']:
            md.write(f"- {lang}: {cnt} commits\n")
        md.write("\n## Commit hour distribution (UTC)\n\n")
        for h, cnt in sorted(analysis['summary']['commit_hours_distribution'].items()):
            md.write(f"- {h}:00 → {cnt} commits\n")
        md.write("\n## Commit day distribution\n\n")
        for d, cnt in analysis['summary']['commit_days_distribution'].items():
            md.write(f"- {d}: {cnt} commits\n")

    print(f"Wrote analysis to {OUT_JSON} and {OUT_MD}")


if __name__ == '__main__':
    if not TOKEN:
        raise SystemExit('GITHUB_TOKEN required in environment to run this script')
    gh = Github(TOKEN)
    analyze_commits(gh, OWNER)
