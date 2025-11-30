import json
from scripts import game_logic


def dummy_analysis():
    return {
        'generated_at': '2025-11-30T00:00:00Z',
        'owner': 'ManoharKonala',
        'repos': {
            'RepoA': {'commit_sample_count': 10, 'stars': 2, 'forks': 0, 'top_languages_by_commits': [('Python', 3)]},
            'RepoB': {'commit_sample_count': 5, 'stars': 0, 'forks': 1, 'top_languages_by_commits': [('TypeScript', 2)]}
        }
    }


def test_compute_xp_for_repo(monkeypatch):
    # monkeypatch to supply test input via file
    analysis = dummy_analysis()
    # write to temp file
    import tempfile, os
    fd, path = tempfile.mkstemp()
    os.close(fd)
    with open(path, 'w') as f:
        import json
        json.dump(analysis, f)
    os.environ['IN_JSON'] = path
    os.environ['OUT_JSON'] = path + '.game'
    # run game_logic
    game_logic.main()
    with open(os.environ['OUT_JSON'], 'r') as g:
        state = json.load(g)
    assert 'total_xp' in state
    assert state['repos']['RepoA']['xp'] > 0
    os.remove(path)
    os.remove(os.environ['OUT_JSON'])
