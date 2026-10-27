# Limitations and experimental boundaries

- **One distribution:** NVIDIA Linux x86_64 595.58.03, with its exact corresponding open-module source. No claim about every release, Windows driver, GRID package or OEM customization.
- **18/18 means source-to-distribution consistency:** six public GB202 archives contribute 18 arrays checked against named symbols in one official driver object. It is not 18 physical-board experiments, an independent second disassembler, or a two-board resident-code measurement.
- **Conditional selection:** bare-metal physical-function operation, ordinary production and confidential computing disabled. Security/debug/CC variants must not be conflated with GeForce-versus-PRO variants. Physical state was not measured.
- **Stored code versus executed code:** common files can branch on SKU, fuses, board firmware or runtime inputs. The comparison establishes no execution trace and no causal setter for instruction throughput.
- **Incomplete security chain:** no matched board-resident mutable FSP firmware, immutable ROM dump, provenance-verified VBIOS pair or exhaustive per-engine microcode inventory.
- **Opaque regions:** boot/FMC bytes were not decrypted or decoded into instructions. Entropy and printable-string counts do not prove encryption. A matching image/hash pair is not an independently validated signature or trust chain.
- **Source semantics:** the selection trace was manually audited against pinned source; byte matching alone does not prove the source-selection interpretation or that either card loaded the files.
- **GEMM and issue rate differ:** PyTorch/cuBLAS throughput depends on algorithms, dispatch, precision, clocks and data movement. It cannot independently identify fuses or expected unlock gain.
- **External hardware evidence:** the PRO reference is a reported 300 W Max-Q, not a matched 600 W Workstation/5090 experiment. Its CSV arithmetic is reproduced, its hardware execution is not. No corresponding privileged configuration captures were identified in that pinned revision. Other branches/history were not exhaustively searched.
- **RM reporting is not a fuse dump:** the inspected getter returns cached information supplied through RM. Header encoding names do not alone establish how a particular Blackwell instruction implements that rate.
- **No hardware work:** no GPU query, benchmark, register read/write, firmware flash, power/clock modification, reset, driver deployment, exploit execution, bypass or unrestricted MMIO sweep was performed. Proposed experiments remain unexecuted.
- **No novelty claim:** shared-file observations already appeared publicly. This package contributes a pinned consistency check, a selection trace and explicit limits; it is not a security vulnerability report.
- **Reproduction inputs:** upstream downloads must remain available. The package does not mirror proprietary inputs. The clean-run record identifies the tested environment; other operating systems and Python versions have not been tested.

See [the report](REPORT.md), [reproduction instructions](REPRODUCE.md), and [publication review](PUBLICATION.md).
