#!/usr/bin/env python3
"""Audit committed files and recompute published CSV summaries; no GPU access."""
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import statistics
import subprocess

root = Path(__file__).resolve().parents[1]
repo = root/'work/sources/blackwell-tensorcore-kernels'
commit = subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()
pin=json.loads((root/'inputs.json').read_text())['repositories']['blackwell-tensorcore-kernels']['commit']
if commit != pin:
    raise ValueError('PRO reference commit differs from pin')
subprocess.run(['git','-C',str(repo),'diff','--exit-code','HEAD','--'],check=True,stdout=subprocess.DEVNULL)
paths = subprocess.check_output(['git','-C',str(repo),'ls-files','-z']).decode().split('\0')
patterns = {
    'privileged_register_or_fuse_capture': r'(?i)\bMMIO\b|\bBAR0\b|FEAT_OVR|FUSE_SS_|read_sm_rates|GET_SM_ISSUE_RATE|/dev/mem|resource0|\bsetpci\b|register[ _-]*(?:dump|capture)|0x0*8238[0-9a-f]+|0x0*8207[0-9a-f]+',
    'firmware_identity':r'(?i)\bVBIOS\b|gsp[_ -]firmware|firmware[ _-](?:hash|version)|gsp_ga10x',
}
files=[]
matches={k:[] for k in patterns}
for rel in filter(None,paths):
    b=(repo/rel).read_bytes()
    files.append(dict(path=rel,size=len(b),sha256=hashlib.sha256(b).hexdigest()))
    if b'\0' in b:
        continue
    text=b.decode('utf-8',errors='replace')
    for key,pat in patterns.items():
        for i,line in enumerate(text.splitlines(),1):
            if re.search(pat,line):
                matches[key].append(dict(path=rel,line=i,text=line))
data=(repo/'results/mma_rate_probe.csv').read_text()
rows=list(csv.DictReader(io.StringIO('\n'.join(l for l in data.splitlines() if not l.startswith('#')))))
medians={variant:{col:statistics.median(float(r[col]) for r in rows if r['variant']==variant)
                  for col in ('ms_per_launch','tflops','flop_per_sm_clk','power_w')}
         for variant in ('f16acc','f32acc')}
result=dict(commit=commit,repository='https://github.com/waynehacking8/blackwell-tensorcore-kernels',
            scope='tracked files at pinned default-branch checkout only; remote branches/history not exhaustively searched',
            files=files,search_patterns=patterns,matches=matches,measured_hardware='reported RTX PRO 6000 Blackwell Max-Q Workstation Edition, 188 SMs',
            medians_recomputed_from_published_rounded_rows=medians,
            ratios=dict(per_clock=medians['f32acc']['flop_per_sm_clk']/medians['f16acc']['flop_per_sm_clk'],
                        wall_clock=medians['f32acc']['tflops']/medians['f16acc']['tflops']),
            interpretation='No privileged-register/fuse captures or firmware identity records found by patterns and manual inspection of tracked source/results. clock64, CUDA/PTX accumulator registers, NVML telemetry and Nsight register counts are present; these are not fuse/privilege-mask readouts.',
            independently_run=False)
(root/'work/results').mkdir(parents=True,exist_ok=True)
(root/'work/results/pro-reference-audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('files','search_patterns')},indent=2))
