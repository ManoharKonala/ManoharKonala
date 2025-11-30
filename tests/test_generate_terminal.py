import json
from scripts import generate_terminal


def test_format_lines():
    lines = ['one', 'two', 'three']
    svg_lines = generate_terminal.format_lines(lines)
    assert 'one' in svg_lines
    assert 'two' in svg_lines
    assert 'three' in svg_lines

