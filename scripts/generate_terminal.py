#!/usr/bin/env python3
"""
Generate a simple SVG 'terminal' based on `data/stats.json`.
"""
import argparse
import json
import textwrap

TERMINAL_TEMPLATE = '''<svg xmlns='http://www.w3.org/2000/svg' width='690' height='300' viewBox='0 0 690 300'>
  <style>
    .bg {{ fill: #0f1724; }}
    .text {{ font-family: 'Fira Mono', 'Courier New', monospace; font-size: 12px; fill: #cbd5e1; }}
    .accent {{ fill: #7c3aed; }}
  </style>
  <rect class='bg' x='0' y='0' width='100%' height='100%'/>
  <g transform='translate(12,24)'>
  {lines}
  </g>
</svg>'''


def format_lines(lines):
    out = []
    for i, line in enumerate(lines):
        y = i * 16
        out.append(f"<text class='text' x='0' y='{y}'>{line}</text>")
    return "\n  ".join(out)


def build_from_stats(stats):
    lines = []
    lines.append("$ whoami")
    lines.append("Konala Venkata Rama Manohar — Pulse. Build. Roar.")
    lines.append("")
    lines.append("$ ls -la projects")
    top = stats.get("repos", [])[:6]
    for r in top:
        lines.append(f"- {r['full_name']} ({r['language']}) ⭐{r['stargazers_count']}")
    lines.append("")
    lines.append("$ cat skills.json")
    langs = {}
    for r in stats.get('repos', []):
        lang = r.get('language') or 'Other'
        langs[lang] = langs.get(lang, 0) + 1
    lines.append(json.dumps(langs))
    return lines


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/stats.json")
    parser.add_argument("--out", default="assets/terminal/terminal.svg")
    args = parser.parse_args()

    with open(args.data, "r", encoding="utf-8") as f:
        stats = json.load(f)
    lines = build_from_stats(stats)
    svg = TERMINAL_TEMPLATE.format(lines=format_lines(lines))
    with open(args.out, "w", encoding="utf-8") as g:
        g.write(svg)
    print(f"Generated terminal SVG at {args.out}")


if __name__ == "__main__":
    main()
