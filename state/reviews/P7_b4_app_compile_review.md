# D214 B4 app compile: source and host review

FINAL PASS, 2026-09-26. Independent review of the implementer and oracle author's artifacts, using a same-model reused context; this is not human or cross-model review. I inspected source and saved evidence only, reconstructed projections as data, and performed no subject import, test, compiler, or device execution. RAW below means state/analysis/P7_b4_app_compile_raw.

## Checked identities

| Artifact | Bytes | SHA256 |
|---|---:|---|
| P7_b4_app_compile_contract.md | 8757 | 76ba6262b2bbdf8ec65359c98488e66befae664d64d5a125c2de65480dda5c06 |
| tools/compile_b4_app_static.py | 24356 | b21527e2cbdb50304ef18d8edd982a5bb8eec6f633d75043bd4e323b7cc59e80 |
| tools/b4_app_compile_remote.py | 7821 | 7dc788cbfb92688d3b1a2343f673da1bae3fa3ade1df5836ae437c013750b2d3 |
| RAW/implementation02.json | 4223 | 52c8f55adb6b7699adab59c18d3776ec92ae45577949aebc7b8c50fc9a719545 |
| tests/tooling/test_b4_app_compile.py | 46224 | 534038c9d38633cb84ab794c3c647942ee5e2e42cf9c02b95b9b9dcb09e022ca |
| RAW/oracle03.json | 117410 | a36d323157a5dd61765fcee909a16777a30ca9560c38635f2c88703d6352d0ab |
| RAW/independent_freeze03.json | 35391 | 0ca70af8f6859a06f5c7c1ed3698651bbca7e01bd61be3d4984cc392be88c473 |
| RAW/coordinator_freeze03.json | 36942 | abfcee5e9385fa75f6d85d02723070c00422714b450b3d1730eec5d9ea2ab527 |
| RAW/host_closing01.json | 33391 | 677401d9bd97e33b7a62b1f21a76d9cb35c3279b18325e4fd53f0082102279d9 |

The 212 independent and 224 coordinator file pins match current bytes. The private caller is 35477 bytes / 06c42406478eb7222364c2cc97a5fcc17154934e8234fda266cf6340c86180e4; all counted replacements reconstruct it. Historical source snapshots remain unchanged.

## Source and oracle findings

The fixed caller admits only ordinary app sources with explicit MATCH=0, MOTORS_ALLOWED=0 and SUMOX_B4_STAND=1; all diagnostic/trial flags remain explicitly zero. The ordinary source mapper, real helper agreement, all original required inputs, seven bootstrap guards, twelve unchanged lifecycle methods, exclusive owners, clean-HEAD admission, durable intent, first-error handling and independent closing remain intact. The D213 policy receives actual checked bytes for all five historical snapshots, through private namespaces, and exact integer M0. Query and compiler metadata still pass the full validators; artifact validation retains ELF, TLS, loader, package/export and identity checks. No profile shortcut or synthetic positive admission replaced those checks.

The amendment solves the original 41318-unit command overflow with two postcompile source-only transfers to the fresh owner's artifact-sources.zlib. The 116347-byte eight-source bundle compresses to 28087 bytes, split 16384/11703. Both writes use anchored no-follow descriptors, exclusive first creation, exact preceding identity/hash for append, bounded readback, regular single-link file/owner/mode checks, ancestry/path/fd stability, and complete descriptor closure. Attempt state is consumed before local packing or dispatch. Complete checked compressed/raw/source pins precede any transported source execution; bounded decompression rejects overflow, incomplete streams and trailing data. The remote checks all eight bundle pins before executing helper/policy bytes. Actual full argv bounds include the terminating NUL; maximum is 29352 units, below 30000.

Incomplete or uncertain transfer attempts now receive an independent read-only partial observation, including local packing failure and lost replies, while remaining failed. A completed second write with a lost reply cannot become success. Existing admission checks may safely refuse before transport; no retry, repair, deletion or privilege expansion was introduced. The final complete read must also pass.

Three original findings were corrected and retained with first evidence in commit 8b669d77: missing dir_fd on the ancestry open (product defect), premature incomplete-transfer closing failure without observation (product/coverage defect), and missing production JSON output framing in the descriptor fixture. The original Linux result was 82 passing and five failed methods, with seven failure records, out of 87. Its confinement rejection was preserved. Revision02 adds four focused lost-reply/partial-read cases, retaining all original methods and assertions; the full-argv check is strengthened from four to five paths.

Revision02 Windows then exposed three fixture-only pwd import errors. Commit 3f6ad8bb preserves that run and oracle. Revision03 changes only the oracle pointer and PortableRemoteContract.setUp: an absent pwd module receives a Windows-only per-case sentinel whose getpwuid and unknown accesses raise; cleanup restores absence. Product bytes, all 91 test bodies, assertion/reject ASTs, skips, fixture projections and all other old function bodies are unchanged. Real Linux account/descriptor behavior is untouched. The portable positives still execute the real checked bundle and D213 artifact validator. No extra skip was added.

The 91 selected cases cover 40 inherited caller, eight ordinary mapping, fourteen remote descriptor, eight B4 integration, sixteen transfer, and five portable remote cases. Negative inputs remain distinct and relevant: stale ordinary/M1/MATCH/short/reordered/extra/Immediate metadata, wrong exact scalar types, each bundle pin, coherent-export/corrupt-ELF input, stale identities, descriptor hazards, timeouts, partial writes and all closing failures. Linux fixtures execute actual I/O programs in owned local trees; portable endpoints are explicitly simulated. They do not establish board behavior.

## Saved host evidence and limits

Coverage is composed, not a new full 91-method run. I reconciled all four intent/result pairs and raw streams, exact method identities, and the sixteen receipt/stream pins in host_closing01.json:

- revision02_linux01: 91 PASS, no skips, 113.029 seconds inner / 127.5224735 outer.
- revision02_windows01: 66 PASS, 22 skips, three pwd setup errors, 139.518 / 139.8464353 seconds; retained unchanged.
- revision03_portable_linux01: the five affected methods PASS, 0.900 / 11.9966694 seconds.
- revision03_portable_windows01: the same five methods PASS, 0.269 / 0.6620033 seconds.

Replacing only the five portable outcomes yields current Linux 91 PASS and Windows 69 PASS plus 22 explicit skips. Every skipped ID has Linux PASS coverage. The other 86 outcomes are reused under the verified exact body/projection equivalence, not relabeled as newly executed. No timeout or unexplained input drift occurred: original revision02's 213-pin closure was stable; its sole subsequent changed file is the reviewed oracle test. Targeted revision03's 224 pins closed unchanged. Both retained Windows temporary directories are actually empty. No independent Linux remnant inventory is claimed. No B4 stage or native output owner existed at closure.

Host driver03 is the exact six declared substitutions from driver02: current freeze/owner/schema and the five-method standard unittest invocation, retaining 600-second bounds, -I -B, isolated temporary roots, exclusive intent and raw outputs. Admission driver03 changes only its freeze pointer from02 to03. The separately reviewed native orchestration retains check-before-execute, failed-check refusal, bounded children, preserved stream/error receipts and three independently attempted closing checks; it has not run.

There is no open source/host blocker. Native admission remains separate: current manifest, fresh board/resource/owner evidence, scope, reviewed committed clean HEAD and check-only must still pass. RAW/native_scope_role_binding02.json (2781 bytes / bf85b1719bc033ec0f87aae3f9d7578a9dd93ab505460a4b6f966bf34294ca28) transparently changes the frozen interface's two obsolete freeze filenames to03 while retaining all seventeen roles; future native admission must bind it. This review establishes host/source readiness only, not a successful target compile, upload, MCU behavior, physical inhibition, WCET or a phase gate. No firmware, wiring or motor permission changes follow.
