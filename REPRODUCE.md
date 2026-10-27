# Reproduce the offline comparison

Requirements: Linux x86_64, Git, curl, POSIX shell, and Python **3.11 or newer** with the standard library. GNU binutils is optional for the independent extraction check. The recorded clean run uses Python 3.14.4 and binutils 2.46. Other versions/platforms have not been tested. Allow approximately 2 GB of local working space plus Git download overhead.

Run from a clean checkout of this repository. Do not run the setup block again over existing `work/` inputs; use a new checkout for a fresh test. No root privileges, installed NVIDIA driver or GPU are needed.

## 1. Retrieve pinned inputs — network required

Only this acquisition stage uses the network. Public research repositories are read as data; none of their tools is run. The expected driver size/hash and commit IDs are in [inputs.json](inputs.json). The checksum confirms integrity against the recorded NVIDIA distribution, not a cryptographic publisher-signature check.

```bash
set -eu
mkdir -p work/downloads work/sources work/results

while read -r name remote revision; do
    git init -q "work/sources/$name"
    git -C "work/sources/$name" remote add origin "$remote"
    git -C "work/sources/$name" fetch -q --depth 1 origin "$revision"
    git -C "work/sources/$name" checkout -q --detach FETCH_HEAD
done <<'PINS'
open-gpu-kernel-modules https://github.com/NVIDIA/open-gpu-kernel-modules.git db0c4e65c8e34c678d745ddb1317f53f90d1072b
gpu-unlock-blackwell https://github.com/phiraml/gpu-unlock-blackwell.git d3326e7dbfe3eff6e0cb8823b2c2d76e701fe95c
gpu-unlock-ada https://github.com/JustAResearcher/gpu-unlock-ada.git d28c485418c3d9d034cd4bac19200bc33dd3453b
vgpu-unlock-blackwell https://github.com/bird/vgpu-unlock-blackwell.git 22d2b112e20981565d543b74745c8c02bf4e8960
blackwell-tensorcore-kernels https://github.com/waynehacking8/blackwell-tensorcore-kernels.git c289bdedb5f256fdf1351de3cacf7757564a0dd0
PINS

curl -fL --retry 2 -o work/downloads/NVIDIA-Linux-x86_64-595.58.03-no-compat32.run https://download.nvidia.com/XFree86/Linux-x86_64/595.58.03/NVIDIA-Linux-x86_64-595.58.03-no-compat32.run
curl -fL --retry 2 -o work/downloads/NVIDIA-Linux-x86_64-595.58.03-no-compat32.run.sha256sum https://download.nvidia.com/XFree86/Linux-x86_64/595.58.03/NVIDIA-Linux-x86_64-595.58.03-no-compat32.run.sha256sum

(cd work/downloads && sha256sum -c NVIDIA-Linux-x86_64-595.58.03-no-compat32.run.sha256sum)
python3 - <<'CHECK_INPUT'
from pathlib import Path
import hashlib, json
pin=json.loads(Path('inputs.json').read_text())['driver']
p=Path(pin['path'])
if p.stat().st_size != pin['size']:
    raise SystemExit('Installer size differs from pinned input')
with p.open('rb') as f:
    if hashlib.file_digest(f,'sha256').hexdigest() != pin['sha256']:
        raise SystemExit('Installer SHA-256 differs from pinned input')
print('Pinned NVIDIA installer size and SHA-256 verified')
CHECK_INPUT
```

Review NVIDIA's [driver license](https://download.nvidia.com/XFree86/Linux-x86_64/595.58.03/license.txt) and [redistribution notes](THIRD_PARTY_NOTICES.md). The next command invokes NVIDIA's archive unpacker **only** in extraction mode; it does not start `nvidia-installer` or install a driver.

```bash
set -eu
sh work/downloads/NVIDIA-Linux-x86_64-595.58.03-no-compat32.run --extract-only --target work/driver-595.58.03
```

## 2. Run offline analysis

After acquisition, the following scripts require no network and no GPU. They never import downloaded research code. Pinned Git commits and tracked-source cleanliness are checked before firmware inspection. Run without an existing modified `work/sources` checkout.

```bash
set -eu
python3 scripts/inspect_firmware.py > work/results/inspection-summary.json
python3 scripts/audit_pro_reference.py > work/results/pro-reference-summary.json
python3 scripts/verify_results.py
```

Expected verification: **18/18 source/package array matches**, **43 derived artifact sizes and SHA-256 values checked**, identical reference metadata apart from the recorded Python version, and recalculated PRO CSV medians/ratios.

`inspect_firmware.py` parses ELF64 headers, section tables and named symbols; converts C byte arrays to bytes; adds a gzip header to the documented raw-DEFLATE/trailer format when needed; validates sizes; compares stored and decoded representations; and recomputes the FMC SHA-384. In ET_REL objects, symbol values are section-relative even when `sh_addr` is nonzero. No decryption, disassembly or signature-chain verification is performed. The SHA-384 is a consistency check with accompanying hash bytes, not an authentication result.

The generated files live under ignored `work/derived/` and `work/results/`. The committed [analysis manifest](analysis/firmware-manifest.json) records their expected relative paths so the files can be located after reproduction. These pointers do not mean firmware bytes are included in the repository.

`audit_pro_reference.py` inventories the pinned tracked files, searches explicit register/fuse/firmware patterns, and recomputes medians from published rounded CSV rows. Its negative search finding is limited to those patterns/files and is supplemented by the documented manual review. It cannot automatically prove absence of all possible capture formats.

## 3. Optional independent section check — offline

Use an explicit disposable output file with `objcopy`: omitting the output argument can rewrite the input. The `-I elf64-little` option permits section extraction with binutils builds that lack a RISC-V target.

```bash
set -eu
readelf -h -SW work/driver-595.58.03/firmware/gsp_ga10x.bin > work/results/gsp-ga10x-readelf.txt
objcopy -I elf64-little --dump-section .fwimage=work/derived/objcopy-fwimage.bin work/driver-595.58.03/firmware/gsp_ga10x.bin work/derived/objcopy-disposable-container.bin
cmp work/derived/objcopy-fwimage.bin work/derived/elf/gsp_ga10x/.fwimage.bin
sha256sum work/driver-595.58.03/firmware/gsp_ga10x.bin work/derived/objcopy-fwimage.bin
```

Expected hashes:

- Container: `bedd3a55614bfa355ea8c7ff6c70adbd75381fe05fde347c00c26ef43f1a0675`.
- `.fwimage`: `78054e4aef5162d540163c8aea529331d27c342f68d500fa81824e31b68bc007`.

No output bytes under `work/` should be committed, attached to an issue, or added to a release. Do not use `git add -f`, archive the working directory recursively, or upload the locally expanded checkout.

## 4. Results that remain external or manual

The selected-file semantics and source trace are manually inspectable through [source excerpts](evidence/source-excerpts.txt) and pinned report citations. They are not established automatically by a hash match. Third-party CUDA measurements, fuse/register observations, VBIOS pairs, actual board load identity and complete FSP firmware remain unreplicated or unavailable. See [limitations](LIMITATIONS.md) and [the clean-run record](evidence/reproduction-validation.json).
