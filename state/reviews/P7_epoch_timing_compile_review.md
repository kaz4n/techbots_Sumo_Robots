# D229 independent current-source native compile review

Reviewed2026-09-27. **PASS: one identified p4_timing M0 static/default build
and its checked native artifacts.** No material blocker was found. This is
compile/link/layout/package acceptance only; it does not establish runtime
p99, worst case, free RAM, stack margin, physical acceptance or a phase pass.
No upload or MCU execution was part of this owner. The reviewer performed
read-only evidence reconciliation and wrote this review only after root
confirmed the compiler process closed. No tests or native commands were run
by the reviewer and no14-profile matrix was repeated.

Native HEAD `ac8be0c7c72141c9507fb74e93beb5f734778d7a`, attempt
`timing_p99_01`, profile p4_timing, exact MOTORS_ALLOWED0 and MATCH0,
`app.ino`, FQBN `arduino:zephyr:unoq:link_mode=static`, source
`13e34a041cbc57db64bec6a51bf3ace2e7527799d3a4d72c1df6c39ce35c8fe1`.
Owner: state/analysis/P7_commissioning_build_raw/commission-p4_timing-m0-6337767d5597.
Board serial2629958581 and boot55c386b9-fe6d-4388-a7f4-1d91e0bb49d8 are
the retained identities. Existing D222 compile-only tooling remains unchanged;
the independent epoch-timing source/host review at this commit remains accepted.
That review was read from Git because the sparse checkout omits its worktree copy.

All135 input pins match both current bytes and this native HEAD's Git blobs.
All105 staged files were read and their sorted path-NUL-content digest
recomputed to the exact source identity above. The new epoch_timing.h
46960d85, runtime.cpp84ad84f3 and runtime.hced423d8 are present in the actual
stage. The before and after remote source maps both match all105 staged hashes.
There is no use of the older pre-D229 image as evidence for these bytes.

The closed result is COMPILE_CHECKED: one property query, one compiler and235
native transports. Root's outer process exited0 after462.907s. Every retained
transport result is0 and every transport stderr is empty. All9 checked remote
children were reaped with returncode0 and timed_out=false. The actual compiler
uses `/usr/bin/arduino-cli --config-file /dev/null`, `--jobs 1`, a720s child
deadline and5s reap. Its JSON and the property-query JSON both report success
with empty compiler_err; all retained compile stderr files are empty.

The actual C and C++ flags enable SUMOX_P4_REACTIVE and SUMOX_TIMING_EVIDENCE,
with B4, P3 drive/turn/stop, P5 abort and motor-fault probe all0. MATCH and
MOTORS_ALLOWED are0. Expanded properties preserve the identified static FQBN,
app.ino, fixed tool/core paths and static default-startup packaging hooks.
The query and compile have empty upload_result objects, and the actual compiler
argv contains no upload option. All9 final checks pass with no first error:
local, identity, initialization, builtins, remote_sources, installed_pins,
overrides, artifacts and artifact_sources. The final artifact reply is
byte-data-equivalent to the original checked packet.

Native artifact checks report STATIC_COMMISSIONING_APP_LAYOUT_PACKAGE_PASS
and STATIC_NATIVE_TLS_LAYOUT_PACKAGE_PASS. All7 build artifacts and the
separate exported flat package are regular and identified; the exported and
build package hashes agree. Loader, TLS source and artifact closing checks all
pass. Weak undefined symbols are empty; the six validated native TLS symbols
remain bound to loader39d4a4fd and source68bb1476.

| Artifact | Bytes | SHA256 |
| --- | ---: | --- |
| Build/export flat package | 91128 | 557bc714513df7a4dc181fff50fa8cd76744cd0519b135d4d7988cc52a6b74ae |
| Raw binary | 91112 | f3cb076030a617bb76ab9e5ef87e75cce965a8a1b57803d63768d5a677841376 |
| ELF | 164832 | e5a998d8bb65eb10316b2eac937930ca363c5274d6a68c0c44bbec472dd251b4 |
| Debug/temp ELF | 1796244 | ed30546b84c3ab12c12f67264b19f688cd1fc5532539679de551fa6363115e01 |
| Map | 460602 | c0398e86bec81c563b07040c34f2a0da686045e2cff36e5e767ef94bccc348e8 |

The checked data-copy extent is208B and initialized BSS170656B. The layout
validator's remaining RAM interval is91280B; Arduino's aggregate size display
reports170868B globals and91276B remaining. These are linker/package accounting,
not measured free memory or stack headroom. The compile proves this current
profile links within its checked artifact bounds; it does not establish a fresh
Runtime object ABI or measured histogram cost.

Principal local receipt SHA256 pins:

- inputs.json14209B: `cfe79671df8d0c6036764ffd5f68f81694920691db20d2bee1dd09edd62b8c10`.
- intent.json1126B: `715806e67b8528fec29ae9b196f72e545beb8735bf17ea917d0903ab289a21cd`.
- result.json1960B: `11c0fa462832104fbe711397769b47bb024f1b55fc3c878547a0df6223fccceb`.
- artifacts.json9733B: `55438b96f166b8a5f0fc0a7565eafd74589c1691d213496f260a928f9b6f6105`.

Accept this source-bound compile result for D229 integration. Historical14-profile
matrix evidence remains historical; this one result covers only p4_timing M0.
P2.2 still needs five-minute all-sensors-live worst-case/p99 evidence and full-loop
cost accounting; the histogram's lifetime prefix of admitted S..C completions
does not itself supply that evidence. No coherent MCU histogram was collected,
no motor run was authorized, and this compile did not replace the D228 recorder
image being diagnosed separately on the board.
