# D241 current production compile-only: actual validation

27 September 2026, Dubai. **COMPILE_CHECKED / artifact layout PASS.**
One native compile-only closed successfully in 413.746 seconds. No upload,
reset, motor operation or source/config change was performed.

The source and tool commit is `6306c88e54353e7864a86656614402631a5a3b9c`;
source digest `9337c580d3451de6f2cfe02ebcaa19abf75b147cf7e35bca34defcc562ed1c3e`.
Attempt `native_match01` consumed owner `match-static-match-m1-1d657ca567ed`.
The frozen worktree is `C:/Users/narut/AppData/Local/Temp/sumox-match-static-native-20260927`.
The prior local check passed in 1.900 seconds. Source/host preparation passed
six focused methods and independent review `01851b69`.

The selected image is the ordinary application with MATCH1/MOTORS_ALLOWED1,
all eight diagnostic flags0, static linking and Immediate startup. Exact FQBN:
`arduino:zephyr:unoq:link_mode=static,wait_linux_boot=no`.
The properties query matched the pinned installed recipes and both package
commands used `-prelinked -immediate`. The full package validator accepted
flag0x06, body/ELF/entry/section/TLS identities and the exported build match.

The current 135 input files match their manifest and reviewed Git blobs;
105 staged files match the staged source map. One properties query and one
compiler ran with the inherited single-job constraint. All235 transports
closed. Nine final checks passed: local source, identity, initialization,
builtins, remote source, installed pins, overrides, artifacts and artifact
source. First error is null.

| Checked artifact | Bytes | SHA-256 |
|---|---:|---|
| app.ino.bin-zsk.bin | 92092 | 7895a4d8991bd2158e63c69cb37ebcdc4f39632311a1dbf47401c3a34f664c86 |
| app.ino.elf | 165836 | ba9766a8a207564fa0d2bd25dd6472a16f176f09740eda4689e167e81536a666 |
| app.ino_debug.elf | 1700052 | 6e09b5fa48739aa32564de4379a48686dd9ccfc545e7d6e34764a560514677d5 |
| app.ino.map | 454962 | 98b25a4c0659dda474307c29d7b75775e2b2d445190c5ff9efd8453190661254 |

The static layout leaves91,280 bytes of RAM and694,340 bytes of flash. These
are image-layout counts, not observed live heap/stack margin or full-loop timing.
The Arduino summary separately reports91,276 bytes remaining; its accounting
differs by four bytes from the structural layout report.
The native artifact directory is
`/home/arduino/sumox26_codex_build/match-static-match-m1-1d657ca567ed/artifacts`.
Checked target files are retained there with the original compiler output.

The [closed raw owner](P7_match_static_raw/match-static-match-m1-1d657ca567ed/result.json)
and its full993 files/1,748,556 bytes were copied exactly to MAIN, with six
outer command/output receipts. `root_copy_closure01.json` binds every copied
leaf. Result SHA-256:
`ca9dc58f111964462d3a4549271dc09f7547e173b905410c261271026df44ee7`.
Independent [actual review](../reviews/P7_match_static_actual_review.md) passed
with no material finding: 6,178 bytes, SHA-256
`dbbac69a05fc449ab06f122354b8fdd0cdb0cccd6f0bab2aea4ade8c198ce590`.
It reconciles all nine checked children as closed/reaped and all saved evidence.
The original child JSON is retained byte-for-byte; convenience compiler JSON
uses Windows line endings with equivalent parsed content. Raw evidence is
committed as `ccd84fe71d5add455d81bda10f4235a837a0ede7`.

The loaded image remains D239's inhibited synthetic recorder. This compile
does not prove Immediate boot execution, native application logging, physical
sensors/motors, initialized WCET/live RAM, cancellation/reopen, a human gate
or motor-run permission. The compile attempt cannot be reused. Future qualified
deployment and fresh identified delivery use the separate D241 guarded tools.
