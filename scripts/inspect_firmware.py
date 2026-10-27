#!/usr/bin/env python3
"""Offline inspection only. No GPU access, firmware execution or decryption.

Run after acquiring the pinned inputs in REPRODUCE.md. Inputs/outputs use work/.
Uses only the Python standard library. Writes extracted bytes under ignored work/derived/; metadata under work/results/.
"""
from pathlib import Path
import collections
import gzip
import hashlib
import json
import math
import platform
import re
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'work/sources/open-gpu-kernel-modules'
PKG = ROOT / 'work/driver-595.58.03'
OUT = ROOT / 'work/derived'
RESULTS = ROOT / 'work/results'
RESULTS.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)
COMMIT = subprocess.check_output(['git', '-C', str(SRC), 'rev-parse', 'HEAD'], text=True).strip()

def require(condition, message='input validation failed'):
    if not condition:
        raise ValueError(message)

def digest(b):
    return hashlib.sha256(b).hexdigest()

def elf64(b):
    require(b[:6] == b'\x7fELF\x02\x01', 'expected ELF64 little-endian input')
    h = struct.unpack_from('<16sHHIQQQIHHHHHH', b)
    shoff, entsz, count, names_idx = h[6], h[11], h[12], h[13]
    require(entsz == 64 and count > 0 and names_idx < count and shoff + entsz * count <= len(b), 'invalid ELF section table')
    headers = [struct.unpack_from('<IIQQQQIIQQ', b, shoff + i * entsz) for i in range(count)]
    ns = headers[names_idx]
    names = b[ns[4]:ns[4]+ns[5]]
    result = []
    for i, s in enumerate(headers):
        name = names[s[0]:].split(b'\0', 1)[0].decode()
        payload = b[s[4]:s[4]+s[5]] if s[1] != 8 else b''
        require(s[1] == 8 or len(payload) == s[5], 'ELF section outside file')
        result.append(dict(index=i, name=name, type=s[1], address=s[3], offset=s[4], size=s[5], link=s[6], entsize=s[9], data=payload))
    return result

pins = json.loads((ROOT/'inputs.json').read_text())
for repo_name, pin in pins['repositories'].items():
    checkout = ROOT/'work/sources'/repo_name
    actual = subprocess.check_output(['git','-C',str(checkout),'rev-parse','HEAD'],text=True).strip()
    require(actual == pin['commit'], 'repository commit mismatch: '+repo_name)
    subprocess.run(['git','-C',str(checkout),'diff','--exit-code','HEAD','--'],check=True,stdout=subprocess.DEVNULL)
installer = ROOT/pins['driver']['path']
require(installer.stat().st_size == pins['driver']['size'], 'installer size mismatch')
require(hashlib.file_digest(installer.open('rb'),'sha256').hexdigest() == pins['driver']['sha256'], 'pinned installer SHA-256 mismatch')

binary_path = PKG / 'kernel-open/nvidia/nv-kernel.o_binary'
binary = binary_path.read_bytes()
bin_sections = elf64(binary)
symbol_map = {}
for section in bin_sections:
    if section['type'] != 2:
        continue
    strings = bin_sections[section['link']]['data']
    for off in range(0, section['size'], section['entsize']):
        name, info, other, idx, value, size = struct.unpack_from('<IBBHQQ', section['data'], off)
        if not size or idx >= len(bin_sections) or idx == 0:
            continue
        symbol = strings[name:].split(b'\0', 1)[0].decode()
        parent = bin_sections[idx]
        # In ET_REL, st_value is section-relative even when sh_addr is nonzero.
        file_offset = parent['offset'] + value
        symbol_map[symbol] = dict(offset=file_offset, size=size)

records = []
def save_record(name, data, **kw):
    p = OUT / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)
    r = dict(id=name, output=str(p.relative_to(ROOT)), size=len(data), sha256=digest(data), **kw)
    records.append(r)
    return r

containers = []
for fw in sorted((PKG / 'firmware').glob('*.bin')):
    b = fw.read_bytes()
    sections = elf64(b)
    header = dict(path=str(fw.relative_to(ROOT)), size=len(b), sha256=digest(b), sections=[])
    for s in sections:
        if not s['name']:
            continue
        r = save_record(f'elf/{fw.stem}/{s["name"]}.bin', s['data'],
                        kind='ELF section', source=header['path'], offset=s['offset'],
                        section=s['name'], selection='GB20x uses this shared .fwimage and .fwsignature_gb20x in ordinary non-CC operation' if fw.stem == 'gsp_ga10x' and s['name'] in ('.fwimage', '.fwsignature_gb20x') else 'not established as selected for the target pair')
        header['sections'].append({k:v for k,v in r.items() if k not in ('selection',)})
        if s['name'] == '.fwversion':
            header['version_ascii'] = s['data'].rstrip(b'\0').decode()
    containers.append(header)

# Parse byte arrays and metadata as data, never import or execute downloaded code.
archive_count = 0
arrays = {}
for f in sorted((SRC / 'src/nvidia/generated').glob('g_bindata_*GB202.c')):
    if 'kgsp' not in f.name:
        continue
    archive_count += 1
    t = f.read_text()
    pattern = r'// FUNCTION: ([^\n]+)\n(?P<meta>.*?)static BINDATA_CONST[^\n]*?\b(?P<symbol>\w+)\[\]\s*=\s*\{(?P<body>.*?)\};'
    for m in re.finditer(pattern, t, re.S):
        meta = m['meta']
        if 'COMPLEX_STRUCT: YES' in meta:
            raise ValueError('struct requires a separate decoder')
        raw = bytes(int(v,16) for v in re.findall(r'0x([0-9a-fA-F]{2})\b', m['body']))
        compressed = 'COMPRESSION: YES' in meta
        data = gzip.decompress(b'\x1f\x8b\x08\x00\x00\x00\x00\x00\x00\x03'+raw) if compressed else raw
        expected = int(re.search(r'DATA SIZE \(bytes\): (\d+)', meta)[1])
        require(len(data) == expected, m['symbol'])
        sym = symbol_map[m['symbol']]
        package_bytes = binary[sym['offset']:sym['offset']+sym['size']]
        require(raw == package_bytes, f'stored package/source mismatch: {m["symbol"]}')
        package_decoded = gzip.decompress(b'\x1f\x8b\x08\x00\x00\x00\x00\x00\x00\x03'+package_bytes) if compressed else package_bytes
        require(data == package_decoded, f'decoded package/source mismatch: {m["symbol"]}')
        original = re.search(r'FILE NAME: (.*)', meta)[1].strip()
        r = save_record('bindata/'+m['symbol']+'.bin', data, kind='decoded bindata',
                       source=str(f.relative_to(ROOT)), source_url=f'https://github.com/NVIDIA/open-gpu-kernel-modules/blob/{COMMIT}/{f.relative_to(SRC)}',
                       original_internal_filename=original, symbol=m['symbol'], stored_compressed=compressed,
                       stored_size=len(raw), stored_sha256=digest(raw),
                       package_binary=str(binary_path.relative_to(ROOT)), package_offset=sym['offset'],
                       package_symbol_size=sym['size'], stored_source_matches_package_byte_for_byte=raw == package_bytes,
                       package_stored_sha256=digest(package_bytes), decoded_source_matches_package_byte_for_byte=True)
        arrays[m['symbol']] = data

require(archive_count == 6 and len(arrays) == 18, 'expected exactly six GB202 archives and 18 arrays')

comparisons = []
def compare(label, a, b, meaning):
    same = a == b
    diff_count = sum(x != y for x,y in zip(a,b)) + abs(len(a)-len(b))
    comparisons.append(dict(label=label, a_size=len(a), b_size=len(b), a_sha256=digest(a), b_sha256=digest(b),
                            identical=same, different_byte_positions_including_length=diff_count, meaning=meaning))

compare('GB20x non-CC vs CC signature section',
        (OUT/'elf/gsp_ga10x/.fwsignature_gb20x.bin').read_bytes(),
        (OUT/'elf/gsp_ga10x/.fwsignature_cc_gb20x.bin').read_bytes(),
        'configuration variant within one container, not consumer versus professional SKU')
compare('GB20x vs GA10x signature section',
        (OUT/'elf/gsp_ga10x/.fwsignature_gb20x.bin').read_bytes(),
        (OUT/'elf/gsp_ga10x/.fwsignature_ga10x.bin').read_bytes(),
        'different chip-family signatures within one container, not consumer versus professional SKU')

base='kgspBinArchiveGspRmBoot_GB202_BINDATA_LABEL_UCODE_'
compare('GB202 boot production vs debug descriptor', arrays[base+'DESC_PROD_data'], arrays[base+'DESC_DBG_data'], 'variant comparison, not RTX 5090 versus RTX PRO 6000')
compare('GB202 boot production vs debug image', arrays[base+'IMAGE_PROD_data'], arrays[base+'IMAGE_DBG_data'], 'variant comparison, not RTX 5090 versus RTX PRO 6000')
for label in ('IMAGE','HASH','SIG','PKEY'):
    compare('FMC production vs debug '+label,
            arrays['kgspBinArchiveGspRmFmcGfwProdSigned_GB202_BINDATA_LABEL_UCODE_'+label+'_data'],
            arrays['kgspBinArchiveGspRmFmcGfwDebugSigned_GB202_BINDATA_LABEL_UCODE_'+label+'_data'],
            'variant comparison; no instruction-level inference from differing opaque bytes')

selected=[]
for r in records:
    if r['id'] in ('elf/gsp_ga10x/.fwimage.bin', 'elf/gsp_ga10x/.fwsignature_gb20x.bin') or r.get('symbol','') in (
        base+'IMAGE_PROD_data', base+'DESC_PROD_data',
        *['kgspBinArchiveGspRmFmcGfwProdSigned_GB202_BINDATA_LABEL_UCODE_'+l+'_data' for l in ('IMAGE','HASH','SIG','PKEY')]):
        selected.append(dict(component=r['id'], rtx5090=r['output'], rtxpro6000=r['output'],
                             sha256=r['sha256'], size=r['size'], identical=True,
                             basis='same source-selected asset under matched ordinary production non-CC configuration; NOT two hardware captures'))

desc = arrays[base+'DESC_PROD_data']
words = struct.unpack('<23I',desc)
boot = arrays[base+'IMAGE_PROD_data']
prod_fmc = arrays['kgspBinArchiveGspRmFmcGfwProdSigned_GB202_BINDATA_LABEL_UCODE_IMAGE_data']
prod_hash = arrays['kgspBinArchiveGspRmFmcGfwProdSigned_GB202_BINDATA_LABEL_UCODE_HASH_data']
fmc_hash_matches = hashlib.sha384(prod_fmc).digest() == prod_hash
compare('production FMC signed image vs corresponding prefix of boot image', prod_fmc, boot[:len(prod_fmc)], 'tests relationship of differently packaged boot assets, not a SKU comparison')

stats=[]
for name,b in [('boot_prod',boot), ('fmc_prod',prod_fmc), ('gsp_rm_fwimage',(OUT/'elf/gsp_ga10x/.fwimage.bin').read_bytes())]:
    c=collections.Counter(b)
    entropy=-sum((n/len(b))*math.log2(n/len(b)) for n in c.values())
    strings=re.findall(rb'[\x20-\x7e]{24,}',b)
    offsets=[]
    pos=b.find(b'\x7fELF')
    while pos != -1:
        offsets.append(pos)
        pos=b.find(b'\x7fELF',pos+1)
    stats.append(dict(id=name, entropy_bits_per_byte=entropy, printable_strings_24plus=len(strings), elf_magic_offsets=offsets,
                      warning='entropy/strings are descriptive only; neither establishes encryption or executable coverage'))
    # Do not emit firmware string samples; publish derived statistics only.

repos={}
for name in ('open-gpu-kernel-modules','gpu-unlock-blackwell','gpu-unlock-ada','vgpu-unlock-blackwell','blackwell-tensorcore-kernels'):
    p=ROOT/'work/sources'/name
    repos[name]=dict(commit=subprocess.check_output(['git','-C',str(p),'rev-parse','HEAD'],text=True).strip(),
                     remote=subprocess.check_output(['git','-C',str(p),'remote','get-url','origin'],text=True).strip())
package_hash=digest((ROOT/'work/downloads/NVIDIA-Linux-x86_64-595.58.03-no-compat32.run').read_bytes())
require(package_hash == (ROOT/'work/downloads/NVIDIA-Linux-x86_64-595.58.03-no-compat32.run.sha256sum').read_text().split()[0], 'official checksum mismatch')
manifest=dict(schema_version=1, client_date='2026-10-27', driver_version='595.58.03', platform_scope='Linux x86_64, offline only',
              python=platform.python_version(), repositories=repos, hardware_observations_performed=False,
              package=dict(path='work/downloads/NVIDIA-Linux-x86_64-595.58.03-no-compat32.run',
                           url='https://download.nvidia.com/XFree86/Linux-x86_64/595.58.03/NVIDIA-Linux-x86_64-595.58.03-no-compat32.run',
                           size=(ROOT/'work/downloads/NVIDIA-Linux-x86_64-595.58.03-no-compat32.run').stat().st_size,
                           sha256=digest((ROOT/'work/downloads/NVIDIA-Linux-x86_64-595.58.03-no-compat32.run').read_bytes()),
                           official_sha256_verified=True),
              kernel_binary=dict(path=str(binary_path.relative_to(ROOT)),size=len(binary),sha256=digest(binary)),
              containers=containers, artifacts=records, selected_assets_comparison=selected,
              variant_comparisons=comparisons, descriptor_words_le32=list(words),
              production_fmc_sha384_matches_published_hash=fmc_hash_matches, readability_observations=stats,
              unresolved_components=['board-resident FSP mutable firmware','immutable Boot ROM bytes','matched VBIOS images','complete other-engine microcode inventory','actual per-board loaded-image measurements','relevant fuse and effective configuration values'])
(RESULTS/'firmware-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
rows=['| Asset | Bytes | SHA-256 |','|---|---:|---|']
for r in selected:
    rows.append(f'| `{r["component"]}` | {r["size"]:,} | `{r["sha256"]}` |')
(RESULTS/'selected-hashes.md').write_text('\n'.join(rows)+'\n')
print(json.dumps(dict(artifacts=len(records),selected=len(selected), source_package_arrays_verified=len(arrays),
                      fmc_sha384_matches=fmc_hash_matches, descriptor_words=words,
                      comparisons=comparisons, readability=stats),indent=2))
