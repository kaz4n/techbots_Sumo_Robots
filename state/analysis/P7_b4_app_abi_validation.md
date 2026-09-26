# B4 file-only ABI preparation

D215 reuses the accepted D209 file-inspection lifecycle for the exact D214 B4
motor-disabled image. It retains the original 185 expressions and adds 128
fixed recorder/stand observations. Four children inspect files; there is no
compiler, upload, reset or MCU read.

The adapter is 32,744 bytes, SHA-256
`4b31dfed3508ebd612abd7de31c5d25e5983c57b802fc55946d3996cf259943d`.
Its derivation preserves seven bootstrap/CLI bodies, twelve parser/loader
bodies and all lifecycle guards. New behavior validates recorder extents,
four-byte indices, enum widths, and the stand fields inside their observed
RobotResult container. It never substitutes ordinary-build addresses.

The first focused host runs passed 20 tests on Linux and 20 on Windows, with
no skips, repairs or retries. The suite includes malformed-marker/numeric/layout
cases, arrays and containment, profile rejection and unchanged-body checks.
No broad inherited suite was repeated. All 153 frozen input files remained
unchanged. Root closure `abi_host_closing01.json`, hash `35323fb4380d9523f3f37d217fe7e7402e3155d3aaec66b574589ee61d02fa13`,
reconciles all 40 outcomes and eight saved invocation files. The Windows
temporary root is empty; no separate Linux remnant inventory is claimed.

Independent source/host review is FINAL PASS:
`state/reviews/P7_b4_app_abi_review.md`, 6,406 bytes,
`3e6ec1d8de5f16d898eb4cf29fe55fe49d80f4d55d27898a9e368dfad4f4ba98`.
The prepared native scope fixes 313 expressions, 21 layouts, seven disjoint
windows, two nested stand subfields, 11 member extents and 73 enum values.
The prospective command is 6,981 Windows UTF-16 units including NUL, below
the retained 30,000 limit. Native admission, clean reviewed HEAD and one local
check-only still precede execution.

The local D214 staging copy is no longer an ABI dependency. Automatic approval
review blocked its removal before execution, so it remains in place. The
blocked-operation receipt is `local_stage_cleanup_blocked01.json` in the raw
directory. There was no alternate deletion attempt.

This is preparation evidence only. The actual B4 ABI is not yet observed.
The following recorder map must use those fresh layouts before a pure decoder
can export retained bytes. Hardware origin, coherent capture, recorder lifecycle,
loss, full initialized timing, live RAM and physical acceptance remain separate.
