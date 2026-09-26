# D198 actual internal SETTLE probe compilation

The single compile-only attempt succeeded at clean reviewed HEAD
`18c1135c5b4602405fdcffa3c7d6fe3dbcd38490`. Check-only and execution returned zero.
The board still runs D195; this operation did not upload firmware or read MCU RAM.

## Execution and retained evidence

Source `117cc0e777341c893f4e618a97e3f196fd0bbf2427cb2a4b02543eb37d6522da`
was built with `arduino:zephyr:unoq:link_mode=static`, default profile and exact
flags `-DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_MOTOR_FAULT_PROBE=1`.
The 129-file manifest is `aa314548521968fd3b1b7b1ef415da3c72c90a6bc914d0a9204ff707bcd7d282`.
One property query and one compiler operation used 238 transports, starting
2026-09-26 06:06:01.438052 UTC and finishing 06:11:52.774054 UTC.
All eight closing checks passed: local, identity, initialization, builtins,
remote sources, installed pins, overrides and artifacts. The compile owner
`app-motor-settle-static01` is consumed and must not be reused.

- [Invocation](P7_motor_settle_compile_raw/native_static01_invocation.json):
  3,560 bytes, SHA256 `fc38c8e10d601588dae8a96240686b77b5c31d88b7dc1d6de2e78cca9cf69fe6`.
- [Result](P7_motor_settle_compile_raw/native_static01/result.json):
  1,608 bytes, SHA256 `9b7f0c445cc84ad6d526445bf8e93ea189f718f0c883da8a1bf5cf077e741af5`.
- [Artifacts](P7_motor_settle_compile_raw/native_static01/artifacts.json):
  9,648 bytes, SHA256 `e18384c14c0b1367667b265ab4c532a4010be65697460a1cd45487bccd9eca10`.

## Checked artifacts

| Artifact | Bytes | SHA256 |
|---|---:|---|
| Raw ELF | 172,840 | `6091f27dbd136e0a694900bc68507b1cc6806073c6bfd50f5e57d892df6daeb9` |
| Debug ELF | 1,839,060 | `dc610650600803c9e36c141e300cdcec478af4f03f4a350669ebe0a4699877b7` |
| Raw binary | 95,504 | `d1033e627420e0de5d8ca90ebdf79c284228a23448f3d3e99130651d5afc65cc` |
| Packaged binary | 95,520 | `e400078166394d0f8ea44b601e9ba2948992c4f263c5c7ee5fb3942433c143d0` |

All eight artifact identities were checked again; the exported package matches.
Static package and native TLS checks passed, with six TLS symbols and no weak
undefined symbols. CLI reports 95,520 bytes of program storage, 171,892 bytes of
globals and 90,252 bytes remaining under its 262,144-byte accounting limit.
Structural validation reports a 90,256-byte RAM tail, 208-byte data copy and
170,664-byte BSS clear range. These accounting quantities do not measure live
free RAM, stack use or worst-case execution time. Differences from the previous
image are not a measurement of the new report's target size or retention.

The native receipt directory retains 1,004 files totaling 1,699,771 logical bytes.
They provide unique command, source identity, compiler and closing evidence.
Target artifacts and staged sources remain required for the next file-only
inspection; no duplicate firmware/debug binaries were downloaded or cleanup
claimed. C: had 20,804,710,400 bytes free at the post-run observation.

## Remaining work

Actual target ABI, the separate report symbol and its emitted publication path
must be observed from these files before a fresh inhibited capture. Historical
addresses and consumed D194/D195/D196 owners cannot be reused. The 150-us and
4,096-poll limits remain unchanged. SETTLE's internal cause, a repair, production
timing, physical acceptance and human phase gates remain unproved.
Independent actual review is recorded in
[P7_motor_settle_compile_actual_review.md](../reviews/P7_motor_settle_compile_actual_review.md).
