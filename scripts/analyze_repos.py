#!/usr/bin/env python3
"""
Gather commit-by-commit language usage, commit time analysis, and repo complexity metrics.
"""
import os
import json
from datetime import datetime
from collections import defaultdict, Counter
from github import Github
import argparse

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


def summarize_repos(gh, owner, sample_limit=100):
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
        # limit sample to sample_limit commits per repo for performance
        for i, c in enumerate(commits):
            if i >= sample_limit:
                break
            sha = c.sha
            # try to get commit details and file list
            try:
                commit_obj = repo.get_commit(sha)
                files = getattr(commit_obj, 'files', []) or []
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
            except Exception:
                # some commits may be inaccessible or partial; ignore
                pass
            commit_count += 1
            total_commits += 1
        analysis['repos'][repo_name]['commit_sample_count'] = commit_count
        analysis['repos'][repo_name]['top_languages_by_commits'] = repo_ext_counter.most_common(3)

    analysis['summary'] = {
        'total_repos': len(repo_list),
        'total_commits_sampled': total_commits,
        'primary_languages_by_commits': overall_ext_counter.most_common(10),
        'commit_hours_distribution': dict(sorted(overall_commit_hours.items(), key=lambda x: x[0])),
        'commit_days_distribution': dict(overall_commit_days),
    }
    return analysis


def output_analysis(analysis, out_json, out_md):
    os.makedirs(os.path.dirname(out_json), exist_ok=True)
    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2)

    # write human readable summary
    with open(out_md, 'w', encoding='utf-8') as md:
        md.write(f"# Analysis Report for {analysis['owner']}\n\n")
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


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--owner', default=os.environ.get('OWNER', 'ManoharKonala'))
    parser.add_argument('--token', default=os.environ.get('GITHUB_TOKEN'))
    parser.add_argument('--out_json', default=os.environ.get('OUT_JSON', 'data/analysis.json'))
    parser.add_argument('--out_md', default=os.environ.get('OUT_MD', 'data/analysis.md'))
    parser.add_argument('--sample_limit', type=int, default=100)
    args = parser.parse_args()

    if not args.token:
        raise SystemExit('GITHUB_TOKEN required in environment to run this script')
    gh = Github(args.token)
    analysis = summarize_repos(gh, args.owner, sample_limit=args.sample_limit)
    output_analysis(analysis, args.out_json, args.out_md)
    print(f"Wrote analysis to {args.out_json} and {args.out_md}")
