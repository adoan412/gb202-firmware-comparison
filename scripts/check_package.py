#!/usr/bin/env python3
"""Offline release-file checks. --write-checksums refreshes the package digest list."""
from pathlib import Path
import argparse
import hashlib
import json
import re

root=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser()
ap.add_argument('--write-checksums',action='store_true')
args=ap.parse_args()
checksum_path='evidence/package-sha256.json'
files=[]
for p in sorted(root.rglob('*')):
    rel=p.relative_to(root)
    if rel.parts[0] in ('.git','work') or '__pycache__' in rel.parts or not p.is_file():
        continue
    if p.is_symlink():
        raise ValueError('Release files must not be symbolic links: '+str(rel))
    if p.suffix.lower() in ('.run','.bin','.rom','.pdf','.zip','.xz','.gz','.o','.so','.ko','.png','.jpg','.pyc'):
        raise ValueError('Unexpected binary/archive in release: '+str(rel))
    b=p.read_bytes()
    if b'\0' in b:
        raise ValueError('Binary content in release file: '+str(rel))
    t=b.decode('utf-8')
    for pattern in (r'/home/\w+/','/'+'Users'+r'/[^/]+/',r'/tmp/'+'gb202-',r'GPU-[0-9a-fA-F]{8}-',r'gh[pousr]_[A-Za-z0-9]{20,}',r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'):
        # The checker source describes the GPU identifier pattern but contains no actual identifier.
        if re.search(pattern,t):
            raise ValueError('Potential private path/identifier/credential in '+str(rel))
    if p.suffix == '.md':
        for target in re.findall(r'\]\(([^)]+)\)',t):
            target=target.strip('<>')
            if target.startswith(('https://','http://','#')):
                continue
            dest=(p.parent/target.split('#',1)[0]).resolve()
            if not dest.is_relative_to(root) or not dest.is_file():
                raise ValueError('Broken or external local link in '+str(rel)+': '+target)
    files.append((str(rel),b))
checks={name:dict(bytes=len(b),sha256=hashlib.sha256(b).hexdigest()) for name,b in files if name!=checksum_path}
if args.write_checksums:
    (root/checksum_path).write_text(json.dumps(checks,indent=2)+'\n')
else:
    saved=json.loads((root/checksum_path).read_text())
    if checks!=saved:
        raise ValueError('Release checksums/file list changed; review changes before refreshing')
print(f'PASS: {len(checks)} release files; relative local links resolve; no binary payloads or detected private paths/identifiers/credentials. Pattern scan is not a proof of absence.')
