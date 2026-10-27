We investigated the RTX PRO 6000 as a GB202 reference for the RTX 5090's FP32-accumulation throughput distinction. This was strictly public-source and offline file analysis; no GPU was accessed or modified.

**VERIFIED, within NVIDIA Linux 595.58.03:** the inspected selection logic maps GB202 to `gsp_ga10x.bin`, its shared `.fwimage`, and `.fwsignature_gb20x` in bare-metal physical-function, production/non-confidential-computing operation. The relevant boot/FMC archives are selected by chip family and security mode; we found no separate 5090-versus-PRO executable in that path.

We also extracted **18 arrays from six public GB202 archives and matched all 18 byte-for-byte to their named symbols in the official driver's `kernel-open/nvidia/nv-kernel.o_binary`**. These are source-to-distribution consistency checks against **one driver object**, not 18 independent comparisons of physical 5090 and PRO 6000 boards. The package records pins, offsets, sizes, SHA-256 values and reproduction commands.

The architecture distinction matters: FSP secure-boots before the host driver; it authenticates and launches GSP-FMC (**First Mutable Code**) on the GSP, which then loads/verifies GSP-RM. The inspected source uses that flow rather than the earlier SEC2 BooterLoad sequence. A default NULL BooterLoad accessor does not establish a hidden Blackwell equivalent.

**UNKNOWN:** matched board-resident FSP/VBIOS bytes, relevant physical fuse values, actual loaded-code identity and runtime branches. Common stored firmware can still implement different policy from different inputs. The PRO Max-Q reference dataset supports equal per-clock accumulation throughput but supplies no identified privileged-register/fuse captures in its inspected revision; its hardware measurements were not rerun here.

Most useful next evidence: matched-driver RM issue-rate responses with board/version provenance, existing validated read-only selector/fuse captures, a matched instruction-throughput probe, and provenance-verified VBIOS comparisons. None alone establishes causation or an unlocking method.

Full report, limitations and reproducibility package: **https://github.com/adoan412/gb202-firmware-comparison**.
