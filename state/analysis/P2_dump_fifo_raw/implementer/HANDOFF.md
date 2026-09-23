# D117 first implementation handoff

Implements the adopted explicit FIFO8 branch in the existing native owner. All
four modified files and contract identity are pinned in first_source_freeze.json;
exact bytes were copied before checks, with no subsequent source changes.

The native owner retains the legacy default path, existing begin/factory signatures,
packet encoding/caps, live-check order and runtime cancellation. FIFO setup uses
three fixed CR1 writes/readbacks, AUTOCR0 admission, immediate TEACK qualification,
conditional mandatory owned-state cleanup and permanent poison retaining first
begin cause. One shared ownedState guard preserves legacy checks and supplies the
setup-only omission of NOT_INITIALIZED/TEACK. FIFO progress uses existing bit7 and
TC semantics with no new pump, timeout or store-count change. Transition identity
uses bounded stack locals; no persistent field beyond root's adopted const enum.

App and recorder select FIFO8 explicitly while keeping the exact previous false/
empty setup statements. Header public prefix remains byte-identical to adoption.
Only private helper declarations were added. Four-file diff is first_scope.diff.

Strict C++17 syntax-only native compilation against existing public native stub
headers passed (-Wall -Wextra -Wpedantic -Werror, no exceptions/RTTI). No old/new
test body was read or executable run. Static review recorded max function51 lines
and all source hashes unchanged from first freeze. No board operation occurred.

Independent tests and separate review remain pending. Root owns recorder and app
default/MATCH compile-only target evidence. Default app's prior conditional model
span456 is a material fit risk; no fit, free-RAM, setup ACK reliability, native
throughput, clean framing, receiver success or physical run authority is assumed.
Retain any test/target failure before a coordinated bounded correction.

## Target-fit repair attempt1

The exact first app ELF0ac42e6c reached conditional ordered loader peak262152,
an8-byte deficit. Reviewer first_app_fit.json preserves the failed final16-byte
export allocation after8 bytes remained. Root approved one representation-only
repair: replace beginFifo's three-element local state table by the same bounded
index-derived0, TE|FIFOEN, UE|TE|FIFOEN values. All guard/write/DMB/readback/cleanup
operations and statuses retain order. No capacities, grants, data layout or timing
changed. Native source is now fdd3df0bff64a510a1333dd906f0aa0a1031214caf1bca0c00508ab7507b27fe;
other three files are byte-identical. Second source bytes were frozen before
checking; second strict native syntax passes. Exact diff and both freezes remain.
Actual target savings/fit require the coordinator's new compile and allocation
audit; syntax alone makes no size or runtime claim.
