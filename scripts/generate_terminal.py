#!/usr/bin/env python3
"""
Generate a simple SVG 'terminal' based on `data/stats.json`, `data/analysis.json`, and `data/game_state.json`.
"""
import argparse
import json
import textwrap
import os

TERMINAL_TEMPLATE = '''<svg xmlns='http://www.w3.org/2000/svg' width='880' height='360' viewBox='0 0 880 360'>
  <style>
    .bg {{ fill: var(--bg, #0f1724); }}
    .text {{ font-family: 'Fira Mono', 'Courier New', monospace; font-size: 12px; fill: var(--text, #cbd5e1); }}
    .accent {{ fill: var(--accent, #7c3aed); }}
  </style>
  <rect class='bg' x='0' y='0' width='100%' height='100%'/>
  <g transform='translate(18,28)'>
  {lines}
  </g>
</svg>'''


def format_lines(lines):
    out = []
    for i, line in enumerate(lines):
        y = i * 18
        # escape xml
        esc = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        out.append(f"<text class='text' x='0' y='{y}'>{esc}</text>")
    return "\n  ".join(out)


def build_from_stats(stats, analysis=None, game_state=None, max_projects=6):
    lines = []
    lines.append("$ whoami")
    lines.append("Konala Venkata Rama Manohar — Pulse. Build. Roar.")
    lines.append("")
    lines.append("$ ls -la projects")
    top = stats.get("repos", [])[:max_projects]
    for r in top:
        lines.append(f"- {r['full_name']} ({r['language']}) ⭐{r['stargazers_count']}")
    lines.append("")
    lines.append("$ cat skills.json")
    # skills from game_state if present, else build from analysis
    if game_state:
        skills = game_state.get('skill_tree', {})
    elif analysis:
        # fallback: build naive skills from analysis
        skills = {}
        for repo in analysis.get('repos', {}).values():
            for lang, cnt in repo.get('top_languages_by_commits', []):
                skills[lang] = skills.get(lang, 0) + cnt
    else:
        skills = {'Unknown': 1}
    lines.append(json.dumps(skills))
    lines.append("")
    lines.append("$ git log")
    # latest activity: show latest commits from stats or analysis
    if analysis:
        commits = []
        for repo in analysis.get('repos', {}).values():
            # don't have commit messages in analysis; use repo_name + count
            cnt = repo.get('commit_sample_count', 0)
            commits.append(f"{repo.get('full_name')}: sampled {cnt} commits")
        commits = commits[:6]
    else:
        commits = [f"{r['full_name']}: last pushed {r.get('pushed_at')}" for r in stats.get('repos', [])[:6]]
    for c in commits:
        lines.append(f"- {c}")
    lines.append("")
    lines.append("$ ./run_portfolio.sh")
    lines.append("Launching portfolio showcase... [animated SVG/GIF]")
    lines.append("")
    lines.append("$ sudo make-me-a-sandwich")
    # easter egg
    if os.path.exists('data/easter.json'):
        try:
            with open('data/easter.json', 'r', encoding='utf-8') as f:
                easter = json.load(f)
                latest = easter[-1]['message'] if easter else '¯\\_(ツ)_/¯'
                lines.append(latest)
        except Exception:
            lines.append('No easter egg found')
    else:
        lines.append('No easter egg found')

    # RPG commands: show XP
    if game_state:
        lines.append("")
        lines.append("$ show_xp")
        lines.append(f"Total XP: {game_state.get('total_xp')}")
        # show top levels
        top_repos = sorted(game_state.get('repos', {}).items(), key=lambda x: x[1].get('xp', 0), reverse=True)[:4]
        for r, s in top_repos:
            lines.append(f"- {r}: XP {s['xp']} | Level {s['level']}")

    return lines


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', default='data/stats.json')
    parser.add_argument('--analysis', default='data/analysis.json')
    parser.add_argument('--game', default='data/game_state.json')
    parser.add_argument('--out', default='assets/terminal/terminal.svg')
    args = parser.parse_args()

    with open(args.data, 'r', encoding='utf-8') as f:
        stats = json.load(f)

    analysis = None
    game_state = None
    if os.path.exists(args.analysis):
        with open(args.analysis, 'r', encoding='utf-8') as f:
            analysis = json.load(f)
    if os.path.exists(args.game):
        with open(args.game, 'r', encoding='utf-8') as f:
            game_state = json.load(f)

    lines = build_from_stats(stats, analysis=analysis, game_state=game_state)
    svg = TERMINAL_TEMPLATE.format(lines=format_lines(lines))

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'w', encoding='utf-8') as g:
        g.write(svg)
    print(f'Generated terminal SVG at {args.out}')


if __name__ == '__main__':
    main()
