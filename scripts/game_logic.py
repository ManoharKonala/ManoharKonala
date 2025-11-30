#!/usr/bin/env python3
"""
Generate a gamified skill sheet and XP using repo stats.
"""
import os
import json
from collections import defaultdict

IN_JSON = os.environ.get('IN_JSON', 'data/analysis.json')
OUT_JSON = os.environ.get('OUT_JSON', 'data/game_state.json')

LEVEL_THRESHOLDS = [0, 50, 200, 500, 1000, 2000]


def compute_xp_for_repo(repo):
    # Basic XP formula: 1 XP per commit sampled + 10*stars + 5*forks
    commits = repo.get('commit_sample_count', 0)
    stars = repo.get('stars', 0)
    forks = repo.get('forks', 0)
    return commits + (10 * stars) + (5 * forks)


def assign_level(xp):
    level = 0
    for i, t in enumerate(LEVEL_THRESHOLDS):
        if xp >= t:
            level = i
    return level


def build_skill_tree(analysis):
    skills = defaultdict(int)
    # aggregate languages and map to nodes
    for repo_name, repo in analysis.get('repos', {}).items():
        langs = repo.get('top_languages_by_commits', [])
        for lang, cnt in langs:
            skills[lang] += cnt
    return skills


def main():
    with open(IN_JSON, 'r', encoding='utf-8') as f:
        analysis = json.load(f)

    game_state = {'generated_at': analysis['generated_at'], 'owner': analysis['owner'], 'repos': {}, 'total_xp': 0}
    total_xp = 0
    for repo_name, repo in analysis['repos'].items():
        xp = compute_xp_for_repo(repo)
        level = assign_level(xp)
        game_state['repos'][repo_name] = {'xp': xp, 'level': level}
        total_xp += xp

    game_state['total_xp'] = total_xp
    game_state['skill_tree'] = build_skill_tree(analysis)

    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, 'w', encoding='utf-8') as g:
        json.dump(game_state, g, indent=2)
    print(f'Wrote game state to {OUT_JSON}')


if __name__ == '__main__':
    main()
