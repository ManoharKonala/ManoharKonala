import os
import json
import tempfile
from scripts import update_stats


def test_summarize_repos_minimal(monkeypatch):
    class DummyRepo:
        def __init__(self, name):
            self.name = name
            self.full_name = f'user/{name}'
            self.description = 'desc'
            self.language = 'Python'
            self.stargazers_count = 0
            self.forks_count = 0
            self.size = 10
            self.pushed_at = None

    class DummyUser:
        def get_repos(self):
            return [DummyRepo('a'), DummyRepo('b')]

    class DummyGH:
        def get_user(self, owner):
            return DummyUser()

    gh = DummyGH()
    stats = update_stats.summarize_repos(gh, 'user')
    assert 'repos' in stats
    assert len(stats['repos']) == 2

