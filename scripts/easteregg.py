#!/usr/bin/env python3
"""
Add an easter egg message to data/easter.json — rotates content weekly.
"""
import os
import json
from datetime import datetime

OUT = os.environ.get('OUT', 'data/easter.json')

MESSAGES = [
    'sudo make-me-a-sandwich — No can do! But here is a sandwich of code 🥪',
    'Konami found: UPUPDOWNDOWN! Matrix mode engaged',
    'Hidden function: approach_neutral(); execute_magic();'
]


def add_easter():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    try:
        with open(OUT, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        data = []
    idx = (len(data)) % len(MESSAGES)
    entry = {"ts": datetime.utcnow().isoformat(), "message": MESSAGES[idx]}
    data.append(entry)
    with open(OUT, 'w', encoding='utf-8') as g:
        json.dump(data, g, indent=2)
    print(f'Appended easter egg: {entry}')


if __name__ == '__main__':
    add_easter()
