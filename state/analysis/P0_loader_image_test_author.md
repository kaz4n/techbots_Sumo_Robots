# P0 independent canonical ELF loader-image tests

Date: 2026-09-22, Asia/Dubai.

Objective: test the supplied pure `loader_image(elfbytes) -> bytes` contract
independently of the capture implementation and any hardware readout. Owned
files are `tests/tooling/test_p0_loader_image.py` and this report. Existing
histogram tests and all production files remain untouched; no loader/capture
implementation or core cpp was read.

Sixteen cases use fabricated ELF32 little-endian ARM headers and program tables,
with explicit scalar packing for the standard 52-byte ELF header and 32-byte
program header. The fixtures are not a captured or uploaded executable. Their
three adjacent file-backed PT_LOAD segments cover exactly 0x08000000 through
0x08040600, exclusive, producing 263680 expected bytes.

The coordinator confirmed physical p_paddr controls load placement. A valid
fixture therefore places one segment at a RAM virtual address but a flash
physical address. Reordered program headers must produce the same canonical
physical image. Extra unloaded debug bytes/non-PT_LOAD data are ignored, while
nonzero file-backed loads outside the flash span fail. Zero-file-size RAM loads
are ignored even when their unused file offset is outside the file. Memory sizes
may exceed file sizes; they must not introduce invented fill bytes.

Positive and negative cases cover exact bytes/length/bytes return type, one-byte
start/interior/end gaps, one-byte overlap, duplicate segments, missing flash
segments, truncated ELF/program tables/payloads, invalid file offsets/sizes,
wrong magic/class/endianness/ARM/version, header and table size/bounds, exactly
32 program headers and rejection of 33. A specific byte at image offset 0x3f8bf
is preserved as supplied: zero remains zero and changing it to 0xff changes the
canonical result. No alignment-byte exception, normalization or omission is
allowed by these expectations.

The existing guarded-import helper is reused without modifying or inheriting
its test cases. It blocks subprocess/network/input actions and checks quiet
import; no main capture command is invoked. Malformed ELF fixtures require
ValueError under the supplied validation contract.

Static handoff: 16 cases; runtime pending coordinator execution when the worker
freezes the implementation. No board connection, actual ELF readout, target
memory comparison, debugger action, upload, existing-file edit or commit occurred.
Passing these pure fixtures will establish parser behavior only, not prove that
a particular hardware image matches its uploaded executable. The exact executable
and target memory identity still require the separate capture workflow.
