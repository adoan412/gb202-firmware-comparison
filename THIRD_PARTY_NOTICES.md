# Third-party materials, attribution and distribution boundaries

## Package contents

This repository includes original analysis utilities, explanatory text, numeric/hash metadata and selected public-source excerpts. It does not contain NVIDIA installers, firmware/payload bytes, object files, board ROMs, decryption material, driver packages, vendor PDFs, research-project binaries, raw issue-comment dumps or firmware string extracts. Reconstructed bytes are local-only outputs under ignored `work/`.

## NVIDIA materials

The [NVIDIA 595.58.03 driver license](https://download.nvidia.com/XFree86/Linux-x86_64/595.58.03/license.txt) distinguishes source-form and binary-form materials. Section 1.1(d) describes conditional distribution of unmodified Linux binary files with the agreement; sections 2.1–2.6 contain firmware/platform, reverse-engineering, modification, notice and security-mechanism restrictions. This project does not rely on a right to redistribute proprietary inputs and does not relicense them. The scripts perform extraction, container/symbol inspection and byte/hash comparison, not decompilation, firmware translation or circumvention. This inventory records the reviewed terms; it does not establish a general license permission for unrelated work.

Public open-module source is separately governed by its per-file notices and [COPYING at the pinned commit](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/db0c4e65c8e34c678d745ddb1317f53f90d1072b/COPYING). The excerpts in `evidence/source-excerpts.txt` are from files bearing NVIDIA's MIT notice. The original notice is retained there; copyright years in the excerpted files include 2021–2025. The original input sources retain their own notices when fetched. No byte-array firmware content is republished as an excerpt.

FSP/GSP-FMC architecture attribution includes [Alexandre Courbot's primary correction](https://lkml.iu.edu/2608.3/02631.html) and [kernel documentation](https://docs.kernel.org/gpu/nova/core/fsp.html). The report identifies the older documentation's naming mismatch rather than adopting it.

## Research credit

- [phiraml/gpu-unlock-blackwell](https://github.com/phiraml/gpu-unlock-blackwell): starting measurements and dispatch investigation.
- [JustAResearcher/gpu-unlock-ada](https://github.com/JustAResearcher/gpu-unlock-ada): API tooling context, earlier-generation research and public Blackwell discussion. This package contains no copied unlock tools or payloads.
- [bird/vgpu-unlock-blackwell](https://github.com/bird/vgpu-unlock-blackwell): reported virtualization investigation, treated separately from tensor-throughput causality.
- [waynehacking8/blackwell-tensorcore-kernels](https://github.com/waynehacking8/blackwell-tensorcore-kernels): published PRO 6000 Max-Q rate source and CSV. Only derived medians/ratios, search results, file hashes and attribution are included; original data are fetched from the pinned upstream revision.
- NVIDIA: official source, firmware distribution and product architecture specifications.

Exact commits and URLs appear in [inputs.json](inputs.json) and [REPORT.md](REPORT.md). Public repository/account names are retained solely for source attribution. Hardware measurements from these projects are credited as reported evidence, not measurements made by this project.

The original portions of this package use the [MIT license](LICENSE). That license does not replace or expand rights in any third-party material or downloaded artifact.
