import json
from scripts import analyze_repos


def test_ext_lang_map():
    assert analyze_repos.ext_to_lang('.py') == 'Python'
    assert analyze_repos.ext_to_lang('.ipynb') == 'Jupyter Notebook'
    assert analyze_repos.ext_to_lang('.unknown') is None

