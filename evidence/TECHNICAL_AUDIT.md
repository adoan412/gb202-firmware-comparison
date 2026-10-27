# Final technical audit

Date: 2026-10-27. Method: a fresh source/wording audit by the same analyst, not a second-person or independent-laboratory review. Reproduction is separately recorded.

## Corrections and clarifications

1. **Citation repaired:** the debug-mode fuse implementation is `kernel_gsp_gb100.c` lines 240–254 at the pinned commit. The earlier report pointed to 270–290, which covers a different fuse-version routine. The revised report and excerpts now target the actual debug check.
2. **Line-bound audit:** the GB202 vGPU initialization citation was shortened to 34–63 to stay within the pinned file. **Dispatch citations expanded:** explicit references were added for prepare/bootstrap dispatch (768–805) and BooterLoad dispatch (1593–1627). The old archive-dispatch range alone did not substantiate those separate claims.
3. **18/18 scope made prominent:** array consistency is between generated public assets and one shipped driver object. It is not an independently observed two-board comparison and does not measure runtime identity.
4. **Security variants separated:** production/debug and non-CC/CC choices are not GeForce/PRO choices. The shared-path finding is conditional on matched mode and release.
5. **Opaque bytes described conservatively:** high entropy and absence of long strings are observations, not proof of encryption or a protection mechanism. No instruction semantics or decrypted-code delta is claimed for those regions.
6. **Incomplete inventories labeled UNKNOWN:** board-resident firmware and other engines are not represented as a complete verified inventory.
7. **Performance inference bounded:** NVIDIA specifications and the PRO Max-Q CSV are external hardware evidence; only the published arithmetic and source are checked here. Different GEMM kernels and clocks cannot isolate issue rate or fuse causality.
8. **RM getter provenance retained:** the host implementation copies cached static information collected through RM. Calling it a direct fuse read would be unsupported.
9. **FSP and GSP-FMC separated:** FSP starts before the driver; GSP-FMC runs on GSP and means First Mutable Code. The report cites a primary correction to older kernel documentation. Neither an architecture diagram nor a NULL fallback establishes a transferable exploit component.
10. **Privacy and portability:** public artifacts use relative local paths. Raw issue-comment JSON, installer/firmware bytes, binary-derived strings and third-party machine IDs are excluded. Public repository names are attribution, not owner identity.

## Script audit

The supplied scripts read local files, parse ELF/byte arrays and CSV, compute hashes, and write only metadata or ignored derived files. They do not import downloaded research modules or execute GPU code. Git subprocesses inspect repository state only. Input acquisition is documented separately; only NVIDIA's checksum-verified archive is invoked, with `--extract-only` and an explicit target. No `sudo`, hardware device access, register operation, kernel build/load, flashing or clock/power setting is required.

The publication version verifies pinned commits, tracked-source cleanliness, installer size/SHA-256, six archives/18 arrays, stored bytes and decoded bytes. It uses checks that remain active under `python -O`. A separate verifier compares regenerated metadata against the committed reference and rehashes generated artifacts. Python version is the only ignored manifest field because it does not determine extracted bytes.

**Limitation:** ELF parsing is scoped to the pinned trusted ELF64 little-endian inputs, not advertised as a hardened general-purpose parser. Shared-path semantics were manually traced in source; metadata identity does not automatically validate those semantics or physical execution.
