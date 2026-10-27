# GB202 Firmware Comparison — RTX 5090 vs RTX PRO 6000

Research date: October 27, 2026 (America/New_York). Scope: public sources and offline Linux x86_64 driver analysis. The source-selection interpretation is for bare-metal physical-function operation, not a guest virtual function. No GPU was queried, benchmarked, reset, flashed, or modified.

## 1. Executive summary

**Scope of the 18/18 result:** these are source-to-distribution consistency checks against one official driver object. They are **not 18 independent comparisons between physical RTX 5090 and RTX PRO 6000 boards**.

**VERIFIED — The inspected NVIDIA 595.58.03 source selects common host-distributed GSP assets for GB202, rather than separate GeForce RTX 5090 and RTX PRO 6000 executable files.** In the ordinary production, non-confidential-computing path, both resolve to `gsp_ga10x.bin`, its shared `.fwimage`, the `.fwsignature_gb20x` section, and the same GB202 production boot/FMC archive families. The extracted GB202 archive bytes were matched to their named symbols in the official driver's `kernel-open/nvidia/nv-kernel.o_binary`. This establishes release-specific distribution and source-selection identity; it is not a capture of either board's execution. [chip-family selector](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/db0c4e65c8e34c678d745ddb1317f53f90d1072b/src/nvidia/arch/nvalloc/common/inc/nv-firmware-chip-family-select.h#L33-L73); [firmware filename selector](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/db0c4e65c8e34c678d745ddb1317f53f90d1072b/kernel-open/common/inc/nv-firmware.h#L82-L111); [generated HAL dispatch](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/db0c4e65c8e34c678d745ddb1317f53f90d1072b/src/nvidia/generated/g_kernel_gsp_nvoc.c#L831-L1030); [FSP image selection](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/db0c4e65c8e34c678d745ddb1317f53f90d1072b/src/nvidia/src/kernel/gpu/fsp/arch/hopper/kern_fsp_gh100.c#L826-L865).

**UNKNOWN — Whether every security-related instruction and initialization input is identical between physical boards.** Board-resident FSP firmware, immutable ROM bytes, matched VBIOS images, actual load measurements, and relevant fuse/effective configuration values were not obtained. “The two cards have identical security firmware” would exceed this evidence.

**SUPPORTED — NVIDIA documents a real accumulation-throughput distinction.** Its GeForce specification lists dense FP16 tensor peaks of 419 TFLOP/s with FP16 accumulation and 209.5 with FP32 accumulation for RTX 5090. Its PRO specification lists equal FP16/FP32-accumulation peaks: 503.8 TFLOP/s for the 600 W Workstation Edition, or 438.9 for the 300 W Max-Q. These are published boost-clock peaks, not measurements from this investigation. [GeForce whitepaper, printed pp. 46–48](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf); [PRO whitepaper, printed pp. 45–47](https://www.nvidia.com/content/dam/en-zz/Solutions/design-visualization/quadro-product-literature/NVIDIA-RTX-Blackwell-PRO-GPU-Architecture-v1.0.pdf).

**INFERRED — The useful next comparison is configuration and initialization evidence, rather than searching for a separate “PRO executable” in these particular host assets.** Identical stored code can execute different branches based on fuses, device identity, board firmware, or runtime inputs. The hypotheses “same bytes” and “different executed instructions” are therefore not mutually exclusive. This result neither establishes an unlocking method nor proves that firmware has no role.

## 2. Evidence labels and matched scope

- **VERIFIED:** Directly checked here through source or offline byte analysis. A verified published file is not an independently verified hardware measurement.
- **SUPPORTED:** A vendor specification or a researcher’s reported observation, not reproduced on hardware here.
- **INFERRED:** A conclusion consistent with the evidence but requiring another observation.
- **UNKNOWN:** Missing evidence or insufficiently established interpretation.

**VERIFIED — Exact distribution inspected:** `NVIDIA-Linux-x86_64-595.58.03-no-compat32.run`, 315,823,191 bytes, downloaded from [NVIDIA's 595.58.03 directory](https://download.nvidia.com/XFree86/Linux-x86_64/595.58.03/). Its SHA-256 is `b66c59b9bebc191b9c21bad7476da1486dd390198223a548892110bca5fb91f9`, matching NVIDIA’s [published checksum](https://download.nvidia.com/XFree86/Linux-x86_64/595.58.03/NVIDIA-Linux-x86_64-595.58.03-no-compat32.run.sha256sum). NVIDIA source tag `595.58.03` resolves to `db0c4e65c8e34c678d745ddb1317f53f90d1072b`. This release was chosen to match one cited project's driver, not as a claim about the newest release.

**VERIFIED — The match is a single unified Linux distribution supporting both product families, with source-selected assets compared across targets.** It is not two independently acquired board-specific packages or two installed-machine captures. Using one distribution removes release/OS package drift; it cannot reveal board-firmware differences. NVIDIA identifies RTX 5090 as device `2B85`, Workstation PRO 6000 as `2BB1`, Max-Q as `2BB4`, and Server Edition as `2BB5` with listed subsystem combinations. The primary product comparison is RTX 5090 versus Workstation PRO 6000; Max-Q is a separate performance reference. [supported products and PCI IDs](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/db0c4e65c8e34c678d745ddb1317f53f90d1072b/README.md#L956-L976). NVIDIA states Blackwell requires the open kernel-module flavor. [595.58.03 open-module documentation](https://download.nvidia.com/XFree86/Linux-x86_64/595.58.03/README/kernel_open.html).

| Repository | Pinned commit |
|---|---|
| [open-gpu-kernel-modules](https://github.com/NVIDIA/open-gpu-kernel-modules/tree/db0c4e65c8e34c678d745ddb1317f53f90d1072b) | `db0c4e65c8e34c678d745ddb1317f53f90d1072b` |
| [gpu-unlock-blackwell](https://github.com/phiraml/gpu-unlock-blackwell/tree/d3326e7dbfe3eff6e0cb8823b2c2d76e701fe95c) | `d3326e7dbfe3eff6e0cb8823b2c2d76e701fe95c` |
| [gpu-unlock-ada](https://github.com/JustAResearcher/gpu-unlock-ada/tree/d28c485418c3d9d034cd4bac19200bc33dd3453b) | `d28c485418c3d9d034cd4bac19200bc33dd3453b` |
| [vgpu-unlock-blackwell](https://github.com/bird/vgpu-unlock-blackwell/tree/22d2b112e20981565d543b74745c8c02bf4e8960) | `22d2b112e20981565d543b74745c8c02bf4e8960` |
| [blackwell-tensorcore-kernels](https://github.com/waynehacking8/blackwell-tensorcore-kernels/tree/c289bdedb5f256fdf1351de3cacf7757564a0dd0) | `c289bdedb5f256fdf1351de3cacf7757564a0dd0` |

## 3. Verified firmware architecture and selection

**SUPPORTED — FSP means Foundation Security Processor and establishes the internal root of trust.** It begins secure boot before the host driver. Its immutable Boot ROM is distinct from mutable firmware it subsequently uses. Kernel documentation describes the ROM-backed root; NVIDIA's GB202 host code explicitly waits for FSP's boot-complete status. This does not establish that all FSP code is immutable or identical across boards. [Linux FSP documentation](https://docs.kernel.org/gpu/nova/core/fsp.html); [GB202 secure-boot wait](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/db0c4e65c8e34c678d745ddb1317f53f90d1072b/src/nvidia/src/kernel/gpu/fsp/arch/blackwell/kern_fsp_gb202.c#L42-L95).

**SUPPORTED — GSP-FMC means First Mutable Code and runs on the GSP, after FSP authenticates and launches it; it then loads/verifies GSP-RM.** It is not FSP's own firmware and not “Firmware Management Controller.” A primary kernel patch explicitly corrects those naming and execution-location errors. The retrieved kernel documentation still contained the older expansion, illustrating why it cannot be copied uncritically. [Alexandre Courbot's architecture correction](https://lkml.iu.edu/2608.3/02631.html).

**VERIFIED — The inspected GB202 source follows the FSP/GSP-FMC path rather than the older SEC2 BooterLoad sequence.** Its generated dispatch selects Hopper-style prepare/bootstrap implementations, while the FSP code prepares the FMC image plus hash, signature and public key. The older `BooterLoadUcode` dispatch has no GB202-specific archive. [Bootstrap dispatch](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/db0c4e65c8e34c678d745ddb1317f53f90d1072b/src/nvidia/generated/g_kernel_gsp_nvoc.c#L768-L805); [BooterLoad dispatch](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/db0c4e65c8e34c678d745ddb1317f53f90d1072b/src/nvidia/generated/g_kernel_gsp_nvoc.c#L1593-L1627). An unused/default NULL stub does not prove that a missing Blackwell Falcon booter is hidden in a closed binary. The GSP “bootloader” archive and signed GFW FMC image are distinct published representations; their filenames do not establish two separate sequential processors or interchangeability. [generated HAL dispatch](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/db0c4e65c8e34c678d745ddb1317f53f90d1072b/src/nvidia/generated/g_kernel_gsp_nvoc.c#L831-L1030); [FSP image and authentication-material setup](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/db0c4e65c8e34c678d745ddb1317f53f90d1072b/src/nvidia/src/kernel/gpu/fsp/arch/hopper/kern_fsp_gh100.c#L990-L1080); [GB202 boot archive](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/db0c4e65c8e34c678d745ddb1317f53f90d1072b/src/nvidia/generated/g_bindata_kgspGetBinArchiveGspRmBoot_GB202.c); [bootstrap source](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/db0c4e65c8e34c678d745ddb1317f53f90d1072b/src/nvidia/src/kernel/gpu/gsp/arch/hopper/kernel_gsp_gh100.c#L780-L830).

**VERIFIED — Selection chain for the matched non-CC production case:**

1. GB202 architecture/implementation maps to firmware family `GB20X`.
2. `GB20X` maps to external filename `gsp_ga10x.bin`. The architecture in that historical filename does not restrict it to GA10x GPUs.
3. The ELF loader takes the common `.fwimage` and constructs `.fwsignature_` + `gb20x`.
4. Generated chip-family dispatch selects the GB202 boot and signed FMC archives for GB202/GB203/GB205/GB206/GB207.
5. Debug state and confidential-computing state can select alternate archives and signature prefixes. Debug state is read from a security fuse in the source; it is not inferred from whether the board is a professional model.

[chip-family selector](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/db0c4e65c8e34c678d745ddb1317f53f90d1072b/src/nvidia/arch/nvalloc/common/inc/nv-firmware-chip-family-select.h#L33-L73); [firmware filename selector](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/db0c4e65c8e34c678d745ddb1317f53f90d1072b/kernel-open/common/inc/nv-firmware.h#L82-L111); [GSP ELF section selection](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/db0c4e65c8e34c678d745ddb1317f53f90d1072b/src/nvidia/src/kernel/gpu/gsp/kernel_gsp.c#L5590-L5718); [FSP image selection](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/db0c4e65c8e34c678d745ddb1317f53f90d1072b/src/nvidia/src/kernel/gpu/fsp/arch/hopper/kern_fsp_gh100.c#L826-L865); [debug-mode fuse selection](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/db0c4e65c8e34c678d745ddb1317f53f90d1072b/src/nvidia/src/kernel/gpu/gsp/arch/blackwell/kernel_gsp_gb100.c#L240-L254).

**UNKNOWN — Actual execution identity.** This source trace establishes what a matching unmodified driver requests under specified conditions. It does not measure firmware overrides, debug/CC state, board revisions, actual loaded bytes, runtime branches, or the earlier board-resident boot chain.

## 4. Inventory and readability

| Component | Availability/provenance | Readability and comparison status |
|---|---|---|
| GSP-RM | **VERIFIED:** official `.run` firmware directory | ELF64 RISC-V outer container; sections and version readable; shared `.fwimage` extracted. Contains readable strings and embedded RISC-V ELF headers, so it is not wholly opaque ciphertext. Full executable coverage not decoded. |
| GB202 GSP boot image + descriptor | **VERIFIED:** NVIDIA generated C arrays and matching driver-binary symbols | Image 290,816 B; descriptor 92 B, version 6, decoded without decryption. Image remains undecoded in this inspection; encryption mechanism **UNKNOWN**. |
| GB202 production GSP-FMC/GFW | **VERIFIED:** NVIDIA generated C archive and matching driver-binary symbols | 287,304 B signed-image bytes plus 48 B hash, 96 B signature, 97 B key. SHA-384 of image matches published hash. This check does not authenticate the signature or its trust chain. |
| Debug FMC and boot variants | **VERIFIED:** same public source and driver binary | Extracted offline; differ from production images. They are security-mode variants, not 5090/PRO variants. |
| CC FMC/concatenated FMC variants | **VERIFIED:** public GB202 archives and matching driver-binary symbols | Included in the manifest; selected conditionally. They must not be relabeled “the PRO firmware.” |
| FSP immutable Boot ROM | **SUPPORTED:** hardware root described in kernel documentation | No external ROM dump obtained; identity across boards **UNKNOWN**. |
| FSP mutable firmware / board boot payloads | **UNKNOWN:** no matched 5090/PRO pair acquired | Not the extracted GSP-FMC. This investigation cannot assign complete GB202 storage layout or compare bytes. |
| VBIOS / board configuration | **UNKNOWN:** no provenance-verified matched pair acquired | Not supplied as two board ROMs in the inspected driver package. Binary and section differences cannot be reported. |
| Other engines / microcode | **UNKNOWN:** complete per-engine availability and loading inventory not established | A complete per-engine GB202 loaded-microcode inventory was not established. No claim that all PMU/graphics/security-engine payloads are identical. |
| SPDM certificates | **VERIFIED:** GB202 L3 and GB20x L2 archive names are public in source | Certificates are not executable throughput-control firmware; not used as causal evidence. |

**VERIFIED — Container inventory:** `gsp_ga10x.bin` is 72,845,296 B, SHA-256 `bedd3a55614bfa355ea8c7ff6c70adbd75381fe05fde347c00c26ef43f1a0675`; `.fwversion` reads `595.58.03`. The separate `gsp_tu10x.bin` is 30,036,864 B, SHA-256 `e908fc362e51900feb5cc5675e887ed9c6ee34c716abc4063ef309a856874d6f`. The latter is a distribution control, not the GB202-selected image. [Complete section inventory](analysis/firmware-manifest.json); [section inspection](analysis/firmware-manifest.json).

**VERIFIED — Extraction versus decryption:** C arrays marked compressed were decoded using their documented raw-DEFLATE-plus-gzip-trailer representation, with expected-size checks. This is decompression, not a cryptographic bypass. Production boot/FMC image arrays are marked uncompressed and have near-uniform byte distributions and no 24-character printable strings. **VERIFIED:** these image regions were not decoded into instructions here. Their entropy does not establish encryption, cipher, protection mechanism, or decryptability. No instruction-level interpretation is claimed for them. [NVIDIA Nouveau extraction utility](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/db0c4e65c8e34c678d745ddb1317f53f90d1072b/nouveau/extract-firmware-nouveau.py); [GB202 boot archive](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/db0c4e65c8e34c678d745ddb1317f53f90d1072b/src/nvidia/generated/g_bindata_kgspGetBinArchiveGspRmBoot_GB202.c); [GB202 production FMC archive](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/db0c4e65c8e34c678d745ddb1317f53f90d1072b/src/nvidia/generated/g_bindata_kgspGetBinArchiveGspRmFmcGfwProdSigned_GB202.c).

## 5. Hashes, byte comparisons and section-level findings

**VERIFIED — Source/distribution cross-check:** all 18 byte arrays extracted from the six `kgsp...GB202.c` archives match the corresponding stored arrays in the official `kernel-open/nvidia/nv-kernel.o_binary` byte for byte. Named ELF symbols provide extraction boundaries; compressed descriptors also match after decompression. There were zero mismatches in the completed run.

**VERIFIED — Selected-asset equality is conditional source-selection equality.** Both target columns resolve to the same artifact under the matched production/non-CC conditions. These are not two measured resident images. Full filenames, array labels, source URLs, package offsets, compressed and decoded hashes are in the manifest.

| Component | Bytes | SHA-256 |
|---|---:|---|
| GSP-RM image (`.fwimage`) | 72,802,304 | `78054e4aef5162d540163c8aea529331d27c342f68d500fa81824e31b68bc007` |
| GB20x non-CC signature | 4,096 | `d2177f6a4bd633dc1d02349c5ed3abd67392c98869d72a7c13569e29391b95bc` |
| GB202 production boot image | 290,816 | `e0d4f6338539a7fdf3254b8a43d71171548e4f4cbd94546b4fc8e23568f9ac1f` |
| GB202 production boot descriptor | 92 | `6f4ecedadb0a7da00feb59a6d8bff7cc428cdfe32ba9b455c067a9393f4c0c91` |
| GB202 production FMC signed image | 287,304 | `960ccfe7c51c0ba3b520801f832474326229c53d51d6f190cd5877a3325e43ef` |
| FMC SHA-384 hash bytes | 48 | `0c7c43d9bc405c2aba64f88e87459f9e12f789cf4172b7ef5c410be56424809c` |
| FMC signature bytes | 96 | `03008489c5fa3a2b555793e8a1555c0ed22465ce8347efa5a5f1ebbcfde88c6a` |
| FMC public-key bytes | 97 | `af870e5dde972840588bfb94a87f94b19ad6659dae6e1343dd0d22f16074ba39` |

**VERIFIED — Section findings:** the shared outer ELF has 17 section headers, including the null entry. There is one `.fwimage`; signatures are named by family and mode, including `.fwsignature_gb20x` and `.fwsignature_cc_gb20x`. There is no separate 5090-versus-PRO `.fwimage` section in this container. `.fwversion`, build ID, symbol/string tables, and section metadata were separately hashed. No per-SKU header, signature, metadata, configuration or executable delta was identified in the selected assets. [GSP ELF section selection](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/db0c4e65c8e34c678d745ddb1317f53f90d1072b/src/nvidia/src/kernel/gpu/gsp/kernel_gsp.c#L5590-L5718); [manifest](analysis/firmware-manifest.json).

**VERIFIED — Real differences exist between unrelated variants.** Production versus debug boot descriptors are identical (92 B), while their 290,816 B images differ at 285,986 positions. Production/debug signed FMC images likewise differ at 285,986 positions; their hashes, signatures and keys differ. These comparisons do not establish different executable instructions: opaque bytes may reflect cryptography or packaging. Different chip-family or CC signature sections also do not establish a consumer/PRO code difference. [Variant comparisons](analysis/inspection-summary.json).

**UNKNOWN — Instruction-level causal differences.** There is no distinct selected per-SKU payload here to disassemble against its counterpart. Byte-identical instruction regions cannot contain different encoded instructions, but differing runtime branches and configuration-dependent behavior remain possible. Complete disassembly/decompilation of the common image was not performed; neither was decryption of boot/FMC regions.

## 6. Existing research and the PRO 6000 reference

**SUPPORTED — `phiraml/gpu-unlock-blackwell` reports RTX 5090 throughput ratios around 0.676 and 0.664.** **VERIFIED:** its inspected benchmark uses PyTorch matrix multiplication with an accumulation-permission toggle, not a register-resident instruction loop. Thus it reports a useful performance symptom, but does not independently read a fuse, establish an issue-rate encoding, or identify firmware causality. A library permission flag does not by itself document the dispatched instruction sequence. [Pinned benchmark source](https://github.com/phiraml/gpu-unlock-blackwell/blob/d3326e7dbfe3eff6e0cb8823b2c2d76e701fe95c/probe/mma_rate.py); [published receipt](https://github.com/phiraml/gpu-unlock-blackwell/blob/d3326e7dbfe3eff6e0cb8823b2c2d76e701fe95c/probe/5090-stock.json).

**SUPPORTED — The Ada project's issue #12 contains reported Blackwell RM rate values and separate register observations, including a GB203 laptop report.** Its reported `fmla32=3` cannot simply be equated with eightfold recoverable application speed. **VERIFIED:** the API header labels 3 as a 1/8 speed-selection code, but the host getter copies cached static information collected through RM; it is not a direct fuse read. Mapping that abstraction to a specific Blackwell instruction and to measured throughput requires validation. The laptop register report is not a matched RTX 5090/PRO 6000 pair. [Issue #12](https://github.com/JustAResearcher/gpu-unlock-ada/issues/12); [issue-rate API definition](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/db0c4e65c8e34c678d745ddb1317f53f90d1072b/src/common/sdk/nvidia/inc/ctrl/ctrl2080/ctrl2080gr.h#L1518-L1582); [issue-rate getter implementation](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/db0c4e65c8e34c678d745ddb1317f53f90d1072b/src/nvidia/src/kernel/gpu/gr/kernel_graphics.c#L3197-L3252); [static issue-rate information collection](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/db0c4e65c8e34c678d745ddb1317f53f90d1072b/src/nvidia/src/kernel/gpu/gr/kernel_graphics.c#L1380-L1411). The public issue is linked rather than republished, to avoid carrying machine identifiers from third-party comments.

**SUPPORTED — `bird/vgpu-unlock-blackwell` reports consumer/GRID binary equality and a failed vGPU initialization involving inaccessible registers.** It investigates virtualization, not the accumulation-rate distinction. Its reported timeouts do not by themselves isolate physical fuse programming from every possible privilege or initialization condition. Its GRID comparison was not independently reproduced here; no GRID package was acquired. The present source/distribution check is a separate narrower result. [Pinned project report](https://github.com/bird/vgpu-unlock-blackwell/blob/22d2b112e20981565d543b74745c8c02bf4e8960/README.md).

### User-supplied `waynehacking8/blackwell-tensorcore-kernels`

**VERIFIED — The inspected revision contains a relevant rate-probe source and published CSV, with no identified privileged-register capture.** The audit covered all tracked files at commit `c289bdedb5f256fdf1351de3cacf7757564a0dd0`, with source/results review and explicit searches recorded in [the audit manifest](evidence/pro-reference-audit.json). No `FUSE_SS`, FEAT override/privilege-mask readout, RM issue-rate getter output, MMIO/BAR capture, or per-board GSP/VBIOS hash record was found. This finding is limited to that checkout; it is not an exhaustive assertion about historical or remote branches.

**SUPPORTED — The reported device is RTX PRO 6000 Blackwell Max-Q Workstation Edition, 188 SMs, 300 W**, rather than the 600 W Workstation model. The published source uses register-resident FP16-input `mma.sync` variants, eight independent accumulator chains and interleaved repetitions, with device-cycle timing. This is more informative about accumulation throughput than comparing different GEMM implementations. CUDA accumulator registers, `clock64()`, Nsight register counts and NVML telemetry are present; none is a fuse or privileged configuration-register capture. [rate-probe source](https://github.com/waynehacking8/blackwell-tensorcore-kernels/blob/c289bdedb5f256fdf1351de3cacf7757564a0dd0/src/mma_rate_probe.cu).

**VERIFIED — Recalculation from the five published, rounded rows per variant:**

| Metric | FP16 accumulate | FP32 accumulate |
|---|---:|---:|
| Median FLOP/SM/clock | 1023.7 | 1023.8 |
| Median wall-clock TFLOP/s | 440.3 | 426.7 |

The per-clock ratio is `1.0000976849` (approximately 1.000); the wall-clock ratio is `0.9691119691`. **SUPPORTED:** this is consistent with equal per-clock accumulation throughput on that reported PRO board. It was not rerun here, does not supply an identically executed RTX 5090 control, and does not prove a fuse mechanism. The probe CSV does not identify a matched driver version, VBIOS, firmware digest or GPU UUID. H100 logs elsewhere in the repository must not be used to fill those PRO-session fields. [published rate CSV](https://github.com/waynehacking8/blackwell-tensorcore-kernels/blob/c289bdedb5f256fdf1351de3cacf7757564a0dd0/results/mma_rate_probe.csv); [clock/power log](https://github.com/waynehacking8/blackwell-tensorcore-kernels/blob/c289bdedb5f256fdf1351de3cacf7757564a0dd0/results/clock_state_rate_probe.txt).

**INFERRED — This reference strengthens the behavior side of the comparison while leaving the firmware/configuration gap open.** Its Max-Q data cannot be directly divided by the unrelated WSL2/PyTorch 5090 result to estimate the gain from changing a hardware setting. Claims about numerical integrity, universal instruction ceilings, or other instruction modes require their own evidence.

## 7. Confirmed findings and remaining inputs

| Question | Result |
|---|---|
| Shared GB202 architecture? | **SUPPORTED:** both vendor architecture tables identify GB202. |
| Same inspected Linux host firmware selection? | **VERIFIED:** same family-selected assets under matched production/non-CC conditions. |
| Public arrays match official shipped bytes? | **VERIFIED:** 18/18 arrays, byte for byte. |
| Entire board security firmware identical? | **UNKNOWN:** FSP mutable payloads, ROM and VBIOS not paired. |
| Same instructions executed over time? | **UNKNOWN:** no execution trace; shared code can branch differently. |
| Relevant fuse words identical/different? | **UNKNOWN:** no matched captures. |
| Effective rates differ on an exact matched hardware pair? | **UNKNOWN here:** vendor distinction and third-party PRO measurements support the premise, but no paired run was performed. |
| Is the PRO reference also a fuse/register dataset? | **VERIFIED:** no such capture identified in the inspected revision. |
| Which component sets the accumulation restriction? | **UNKNOWN:** host selection and performance evidence do not isolate the setter. |
| Does firmware equality prove hardware-only enforcement? | **INFERRED:** no; shared firmware may enforce policy from different inputs. |

**VERIFIED — Model-dependent initialization is real in the inspected host code.** `kernel_gsp_gb202.c` checks PRO device/subsystem combinations to choose vGPU heap/partition parameters; `2B85` is absent from that allowlist. **UNKNOWN:** whether an analogous branch sets math-throughput configuration. This vGPU example establishes that shared code plus different inputs is an implemented pattern, not that this particular branch explains tensor performance. [GB202 model-dependent vGPU initialization](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/db0c4e65c8e34c678d745ddb1317f53f90d1072b/src/nvidia/src/kernel/gpu/gsp/arch/blackwell/kernel_gsp_gb202.c#L34-L63).

## 8. Assessment of the four hypotheses

| Hypothesis | Assessment |
|---|---|
| A — Identical firmware, different hardware configuration | **INFERRED: leading next avenue for the host-distributed assets.** Shared payloads are established conditionally; actual fuse differences and their causal role remain unverified. Cannot generalize equality to all firmware. |
| B — Different firmware instructions | **UNKNOWN for execution and board-resident code; no evidence of a distinct per-SKU executable in the inspected selected assets.** Common stored code can execute different instructions through branches, so this is not the opposite of A. |
| C — Identical firmware and relevant fuses, different effective configuration | **UNKNOWN.** Its same-fuse premise has not been demonstrated. Even matching a few visible words would not establish identical complete security state. |
| D — Comparison adds no information | **INFERRED: too strong for this investigation.** Source-selection tracing, shipped-array equality, component separation and the PRO-reference audit narrow the next work. Parts of the shared-image finding were already public, so no novelty priority is claimed. |

## 9. What Evidence Would Advance This Investigation?

See [the proposed evidence plan](NEXT_EVIDENCE.md). Its priorities are matched-driver RM issue-rate observations, existing validated selector/fuse evidence, matched instruction throughput, and provenance-verified VBIOS comparisons. These are proposals only; no hardware experiment or driver modification was performed.

## 10. Reproducibility and limits

The scripts inspect files only. [Reproduction instructions](REPRODUCE.md) record acquisition and extraction commands. [Firmware manifest](analysis/firmware-manifest.json) records sizes, SHA-256, source URLs, C symbols, driver ELF offsets, decompression, section boundaries and comparisons. [Source excerpts](evidence/source-excerpts.txt), [pinned input provenance](inputs.json), [tool versions](evidence/tool-versions.txt), and [PRO-reference audit](evidence/pro-reference-audit.json) accompany the report. No research project's hardware scripts, payloads, kernel modules or benchmarks were executed. The public package excludes installer, firmware, object, PDF, and raw issue-comment copies; derived bytes are regenerated only under ignored `work/`. See [limitations](LIMITATIONS.md), [technical audit](evidence/TECHNICAL_AUDIT.md) and [redistribution notes](THIRD_PARTY_NOTICES.md).

**INFERRED — Answer to the final research question:** this comparison provides a useful narrowing result: the inspected host-distributed firmware path does not supply a separate RTX PRO 6000 executable to explain the advertised throughput distinction. That increases the value of comparing validated configuration inputs and effective state. It does **not** establish complete security-firmware identity, rule out configuration-dependent firmware behavior, or establish that an unrestricted configuration is transferable.
