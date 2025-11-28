#!/usr/bin/env python3
"""
Utility helpers for processing data and sanitizing repo metadata.
"""
import re


def sanitize_markdown(s):
    if not s:
        return ""
    # Remove dangerous tags and reduce whitespace
    s = re.sub(r'<[^>]+>', '', s)
    s = s.strip()
    return s


if __name__ == '__main__':
    print('helpers')
