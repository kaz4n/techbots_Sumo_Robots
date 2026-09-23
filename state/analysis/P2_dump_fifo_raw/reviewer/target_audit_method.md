# D117 exact target audit preparation

Prepared 2026-09-24 before D117 artifacts exist. No target PASS is implied.
Reused separate same-model source-aware reviewer; no board operation, production
or test edit. The coordinator owns collection. Apply the existing ELF decoder
and installed-loader model; do not create a new modeling framework.

## Collector review and requested addition

Initial wrapper `P2_dump_fifo_target_collect.py` SHA256
`e16db85d247a54284a4f44840f58f3da09cdfe7b65553b922fb125ce0f5b99c2`
selects only recorder default or app default/MATCH, requires an exact source
digest, and redirects existing collectors to D117 evidence. Its delegated
programs inspect completed board-Linux files/offline ELF data, not the MCU.
No compile, upload, reset or capture action is introduced. Keep its exact
dependency identities from `coordinator/collector_static.json` with each run.

The recorder collector already preserves sizeof and complete ptype/o for
UnoQDumpPort, Runner, Transaction, Transfer, Report and associated types, with
C++ language and max-value-size unlimited. Its three ELFs/ZSK,15 ELF commands
and one ABI command are sufficient for the existing D116 audit adaptation;
adding native alignof makes that aspect explicit.

The app chain currently queries GDB only against the loader for exports. It does
not query app.ino_debug.elf for the new native object's layout. Required narrow
addition, reported to root before collection: one offline GDB command per app
profile, bound to the exact checked build/app.ino_debug.elf, with -nx -nh -batch,
C++ language and max-value-size unlimited. Record sizeof/alignof and ptype/o
recorder::dump::UnoQDumpPort, including its new buffering_ member. Include
Runtime/Transaction/DumpPort/Transfer layout/size to establish unchanged owner
composition and per-profile differences. Retain exact command, status, stdout,
stderr and debug-file/tool identity; a failed query must not become a successful
ABI receipt. This can be a D117-only supplementary query; old collectors need
not acquire a new general feature.

Closure before collection: corrected wrapper SHA256
`e8c23dcbd73c59c1014720f82d5f8bcd5ff42d9c555b96d0262c42377379cf3c`
implements this exact app query, using supported `alignof(T)`, five explicit
types, fixed installed GDB, inner30s/outer60s timeouts, exact debug hash before
and after, and a finally-written command receipt on failure. Its offline literal
contains no run/attach/target command. Reviewer AST/compile-only checks pass in
`source_static.json`; no module or embedded command was executed by reviewer.
Coordinator `collector_abi_static.json` binds the corrected bytes, preserving
the initial wrapper and rejected `__alignof__` primitive syntax evidence.
No further collection field is required before the actual three artifacts.

The selected constexpr owner may move from .bss into initialized .data. Do not
require a BSS symbol or assume the old204-byte size, old member offset, or padding
reuse. Decode raw ET_REL st_value relative to its actual section; nm's displayed
VMA must not be subtracted from that value.

## Source, receipt and artifact identity

1. Revalidate each unique checked receipt, exact project/FQBN/flags/default or
   Immediate setting, command argv, installed hashes and empty-library policy.
   Recorder admits only bench-default with M0; app profiles are bench-default
   M0 and match-immediate M1. This is compile-only even for the M1 artifact.
2. Rehash every frozen source byte and recompute its ordered digest. Expect95
   recorder files and91 app files. Against D116's exact90 shared files, only the
   two dump-native files may differ;88 shared files must match. Each project's
   own sketch has its independently reviewed explicit FIFO constructor change.
   No new source/module/test/config file is staged by D117.
3. Do not demand total source equality to the older D108 app snapshot: D109–D112
   already added unrelated bench constants to config. Use D116's frozen shared
   source for current identity and D108's exact per-mode app ELF for previous
   import/layout/loader comparisons, disclosing the distinct baselines.
4. Bind all three ELF bytes and the ZSK to checked receipt/collector hashes.
   Final ELF and ZSK alone are candidate deployment artifacts. Preserve all
   initial failed compilations/queries/fit models; never substitute a later file
   under an earlier source digest or mark a debug/temp model as a deployment.

## Startup, ownership and machine-code checks

Inventory every init/preinit/fini entry and static-thread bound. Require the
existing strong empty __loopHook and actual empty initVariant; the latter may
remain weak. Inspect main's relocations and its selected actual hook bodies.
No new thread, IRQ/DMA service, Bridge/router/RX handler or native owner is allowed.

Inspect constructor instructions and/or initialized object bytes to prove both
existing native owners select FIFO8 while construction remains passive. Do not
require a dynamic constructor call when constexpr initialization legitimately
places a mode byte in data. Verify the exact enum storage using debug ABI and
the actual section bytes. Preserve owner identity in the unchanged factory
callbacks; inspect their references and all mode-dependent native entry points.

For recorder, inspect actual setup's false/empty arguments and Runner's disabled
branch/terminal poll: no owner callback or clock. For app, inspect unchanged empty
SetupGrants and no new native-dump setup/readiness/write. The entire app setup is
not passive: unchanged Runtime.begin first initializes Transaction/MotorGate and
samples its clock before optional source/dump grants. Preserve that distinction;
neither M0 nor absent optional grants establishes no pin I/O or permission to run.

Resolve every relocation-used external against pinned loader exports, separating
unused imported declarations and debug metadata from runtime dependencies. App
retains its existing motor/sensor owners; recorder must retain only its declared
inert motor and existing UART owner. No new heap allocator, hidden setup callback,
thread import use or foreign owner may appear. Preserve the existing abort-only
exception allocation shim and shared native pin table where the app uses it.

Compare relevant legacy routines and callback bindings to the actual source
diff and old artifact; setup/live ownership/cleanup bodies legitimately change
only as reviewed for the selected mode. Compare final/debug functions exactly;
for temporary artifacts normalize only relocation slots whose linked values
actually differ. THM_CALL/MOVW/MOVT bytes/relocation identities must be accounted
for rather than rejected as unknown or zeroed indiscriminately. Record symbol
aliases, code-size changes and data migration explicitly.

## Ordered loader model and acceptance

Use the existing `state/reviews/P2_bridge_dependency_review_raw/elf_review.py`
SHA2561456224b9a6fa949fefb0abf6c80b7e461508ab6dc0d8063d3ff9e1235f21123
and loader ELF SHA25639d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd.
Revalidate the installed32-bit non-Harvard256KiB configuration and persistent
flash-peek alignment at0x08100010. Any changed premise requires an explicit new
analysis; it cannot be silently absorbed into the prior model.

Keep the ordered allocation ledger:88-byte initial bookkeeping; extension;
section map; copied .text/.data/.rodata/.bss/.exported_sym/.preinit_array/
.init_array/.fini_array in actual loader order; temporary globals and export
copy. Account payload, alignment/prepadding, allocator headers and rounded
chunks. Explain any additional copied section. Require each allocation to fit
the remaining contiguous span; report peak, span and largest payload separately
from compiler RAM. Retain negative results without relaxing buffers/timeouts.

D116 recorder baseline: payload216932, peak220280, span41864/largest41860.
D108 app default: peak261688, span456/largest452; MATCH peak260056, span2088.
These are comparison values, not budgets that the new object automatically
inherits. Debug/temp images may exceed the pool and remain separately labeled;
only the final selected image must satisfy deployment-format conditional fit.

The final ZSK check must allow length bytes appropriate to its actual size;
verify encoded length and exact bytes after the16-byte header instead of copying
a small-ELF list of changed header offsets. Retain any reviewer harness failures
and their precise correction without changing product bytes or prior evidence.

Even a passing final audit is conditional on pristine heap, successful peeks and
no interleaved/constructor allocations. It proves neither live free RAM/stack,
setup ACK reliability,80us effective service rate,800us whole tick, framing,
receiver delivery, physical ownership grants, motor permission nor a human gate.
Final source/test/target verdict awaits actual frozen implementation, independent
tests and exact artifacts; no unknown future image is approved by this plan.
