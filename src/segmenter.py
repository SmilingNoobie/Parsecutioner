import re
from rapidfuzz import process, fuzz

HEADERS = ['education', 'experience', 'skills', 'projects', 'publications']

def find_headers(lines: list) -> dict:
    indices = {}
    for i, line in enumerate(lines):
        key, score, _ = process.extractOne(line.lower(), HEADERS, scorer=fuzz.token_sort_ratio)
        if score > 80:
            indices.setdefault(key, []).append(i)
    return indices


def segment(text: str) -> dict:
    lines = text.splitlines()
    header_idxs = find_headers(lines)
    segments = {}
    sorted_headers = sorted(header_idxs.items(), key=lambda x: min(x[1]))
    positions = [(len(lines), None)]
    for header, idxs in sorted_headers:
        for idx in idxs:
            positions.append((idx, header))
    positions = sorted(positions, key=lambda x: x[0])
    for i in range(len(positions)-1):
        start, header = positions[i]
        end, _ = positions[i+1]
        content = '\n'.join(lines[start+1:end]).strip()
        segments.setdefault(header, []).append(content)
    return segments
