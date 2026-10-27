Thank you for publishing the Blackwell measurements and dispatch evidence. We used them as a starting point for a separate offline GB202 comparison.

In NVIDIA Linux 595.58.03, we verified the common GB202 host-firmware selection path under matched bare-metal physical-function, production/non-CC conditions, and matched 18 public GB202 archive arrays byte-for-byte to their named symbols in the official driver object. These are source-to-distribution checks, not paired physical-board measurements.

One architectural clarification may help narrow the search: the inspected GB202 path uses FSP to authenticate and launch GSP-FMC (First Mutable Code) on the GSP, which loads/verifies GSP-RM. The default NULL SEC2 BooterLoad accessor does not establish that an equivalent Blackwell Falcon image must reside in the closed object. That inference remains unproven; the FSP/GSP-FMC path merits being treated separately.

Shared stored assets still allow different runtime branches or configuration inputs. We have not established board-resident FSP/VBIOS identity, fuse causality, or an unlock path. The report documents the evidence and limits rather than duplicating them here: **https://github.com/adoan412/gb202-firmware-comparison** (see REPORT.md and REPRODUCE.md).
