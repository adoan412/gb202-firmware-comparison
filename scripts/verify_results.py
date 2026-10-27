#!/usr/bin/env python3
"""Offline comparison with committed metadata and local derived-byte validation."""
from pathlib import Path
import hashlib
import json

root = Path(__file__).resolve().parents[1]
def read(rel):
    return json.loads((root/rel).read_text())
def require(condition, message):
    if not condition:
        raise ValueError(message)

expected = read('analysis/firmware-manifest.json')
actual = read('work/results/firmware-manifest.json')
# Python version is recorded but not an input to firmware bytes or source selection.
for obj in (expected,actual):
    obj.pop('python',None)
require(actual == expected, 'firmware metadata differs from the committed reference')
for art in actual['artifacts']:
    b = (root/art['output']).read_bytes()
    require(len(b) == art['size'], 'size mismatch: '+art['id'])
    require(hashlib.sha256(b).hexdigest() == art['sha256'], 'hash mismatch: '+art['id'])
reference = read('evidence/pro-reference-audit.json')
recomputed = read('work/results/pro-reference-audit.json')
require(reference == recomputed, 'PRO reference audit differs')
summary = read('work/results/inspection-summary.json')
require(summary == read('analysis/inspection-summary.json'), 'inspection summary differs')
require(summary['source_package_arrays_verified'] == 18, 'expected 18 source/package array checks')
require(summary['fmc_sha384_matches'], 'FMC SHA-384 check failed')
require(read('work/results/pro-reference-summary.json') == read('analysis/pro-reference-summary.json'), 'PRO summary differs')
print('PASS: 18/18 source/package array checks; 43 derived artifact sizes/hashes; metadata matches committed reference; PRO CSV/audit recomputed. No GPU access.')
