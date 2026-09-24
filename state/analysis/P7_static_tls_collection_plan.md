# D146 bounded read-only TLS provenance collection

Previous turn made verified progress: D145 collected the exact failed ELF and
identified six absolute TLS symbols; D144 remains rejected. Active P7 continues.
No reuse of either consumed experiment is proposed, and no compiler is needed.

After separate inspection and coordinator adoption under D051, execute the fixed
`P7_static_tls_raw/collect_existing.py` once using Windows Python `-B` from this
repository. The launcher must hash-check its captured bytes before execution.
Current draft SHA256: `2443cedc54e6df3f11249780fb7fb5a787612ea1dc88ad0a8d563fc404d8d31c`.
It pins its remote read composition to
`48ca3cdf0ef2eda317ceb58cd841ee53fa21ff92336abfd2212005cc6b4f8b6e`.
Both compositions have syntax-only AST checks; neither has executed.

This is a fixed diagnostic composition of unchanged D143 transport, bootstrap,
descriptor/file/claim checks and local postchecks, not a reusable new build tool.
Separate source inspection covers the new glue. All17 original inputs, source
stage, three historical receipts, exact ADB executable/serial and process-local
transport configuration remain checked. Use a fresh exclusive `observed/` path.

One remote Python invocation reads only existing files. It checks the original
D144 boot/directory Claim and all eight exact artifact FileRecords before and
afterward. The installed packaged firmware must still hash to39d4a4fd. Read the
installed `variants/arduino_uno_q_stm32u585xx/tls-syms.S` (maximum64KiB), exact
original map and debug/temp ELF forms (maximum16MiB each). The original debug
and temp forms have identical hashes; return only one payload after independently
checking both files. Read `build/core/tls-syms.S.o` (maximum1MiB) only if that
exact absolute candidate is present in the checked map. Otherwise explicitly
report unresolved object provenance and do not search or guess another path.

Original helper functions prevent linked/nonregular/unstable reads. Recheck
installed firmware, assembly and any observed object identity/hash at the end.
Keep compressed payloads in the original command receipt (maximum2MiB response);
host decoding is bounded and hash/length checked. Decoded files are saved
exclusively only after successful response and independent local postchecks.
Preserve the first failure; no retry follows a failed or uncertain observation.

There is no remote subprocess/compiler, write, upload, reset, inferior or MCU
execution. The only process invoked remotely is Python for file inspection.
No validator, frozen contract/oracle, production policy or firmware change.
Collection status proves bytes/provenance only, never static admission or runtime.

After collection inspect the actual map/object and compare the six symbol rows
across existing ELF forms. The installed assembly and packaged firmware provide
the required source link; the map/object provide input provenance. Use local
readelf/Arm objdump read-only, retaining compact conclusions. A later admission
amendment, if justified, needs separate reviewed scope and independent tests.
