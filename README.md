# GB202 Firmware Comparison — RTX 5090 vs RTX PRO 6000

An offline, release-specific investigation of NVIDIA's Linux **595.58.03** firmware distribution and source-selection logic. This is an architectural comparison, not an unlock implementation.

**VERIFIED:** for matched bare-metal physical-function, production, non-confidential-computing conditions, the inspected GB202 source selects the same host-distributed GSP container, image/signature section and GB202 boot/FMC archive families for both products. **18/18 public byte arrays match their stored copies in one official NVIDIA driver object. These are source-to-distribution checks, not 18 independent physical-board comparisons.**

**UNKNOWN:** whether the cards' entire security firmware, runtime instruction paths, fuse state or initialization inputs are identical. Board-resident FSP firmware, ROM/VBIOS pairs and actual load measurements were not compared. Shared stored code can execute different branches.

**SUPPORTED:** NVIDIA publishes different FP32-accumulation throughput ratios for the products. The third-party PRO 6000 Max-Q dataset inspected here reports equal per-clock rates; no corresponding privileged-register/fuse capture was found in that pinned checkout. Those hardware results were not reproduced here.

Read the [complete report](REPORT.md), [limitations](LIMITATIONS.md), and [next evidence plan](NEXT_EVIDENCE.md). Claim labels distinguish direct file/source checks (**VERIFIED**), external reported evidence (**SUPPORTED**), reasoning (**INFERRED**), and missing evidence (**UNKNOWN**).

## Reproduce

Follow [REPRODUCE.md](REPRODUCE.md) to retrieve pinned source commits and the checksum-verified installer from NVIDIA, unpack it without installing, and run standard-library Python analysis. No GPU, root access, driver installation, CUDA workload or experimental module is required. The supplied Python scripts are offline; only the documented input-acquisition commands use the network. The official installer is invoked only in extraction mode after integrity verification.

The clean reproduction status and external-link checks are in [the publication checklist](PUBLICATION.md). NVIDIA installer, firmware and object binaries are **not included**. Reconstructed bytes stay in ignored `work/` and must not be committed or uploaded. See [redistribution and credit notes](THIRD_PARTY_NOTICES.md).

## Contents

- [REPORT.md](REPORT.md): complete findings and source citations.
- [inputs.json](inputs.json): driver size/hash and pinned upstream commits.
- [analysis/firmware-manifest.json](analysis/firmware-manifest.json): component/section provenance, hashes, offsets and conditional selection records.
- [analysis/inspection-summary.json](analysis/inspection-summary.json): source/distribution and variant results.
- [evidence/pro-reference-audit.json](evidence/pro-reference-audit.json): tracked-file audit and recalculated published CSV statistics.
- [evidence/TECHNICAL_AUDIT.md](evidence/TECHNICAL_AUDIT.md): corrections and evidence boundaries.
- [scripts/inspect_firmware.py](scripts/inspect_firmware.py), [scripts/audit_pro_reference.py](scripts/audit_pro_reference.py), [scripts/verify_results.py](scripts/verify_results.py): offline utilities.
- [drafts/issue-86-comment.md](drafts/issue-86-comment.md) and [drafts/phiraml-notification.md](drafts/phiraml-notification.md): unposted outreach drafts, with a repository-link placeholder.
- [PUBLICATION.md](PUBLICATION.md): review checklist and optional publication commands.

The result narrows the search within the inspected host assets. It does not establish fuse causality, transferable privileges, or identical firmware execution on physical boards.
