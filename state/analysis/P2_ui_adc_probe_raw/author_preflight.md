# D114 bounded independent public preflight

2026-09-24. Draft only; no adoption, implementation, decoder execution or hardware
action follows. The author read `P2_ui_adc_probe_contract_draft.md` only, using
prior public D112 contract/header context. No production body was read.

The wrapper and staging expectations are independently testable without another
firmware abstraction: one existing Native/Runner; one begin with Grants{true};
one poll per loop; compile guards; exact four-file reuse; and unchanged default
false-grant sketch. An opaque actual-wrapper host test can count its owner calls.
Staging tests can compare source bytes/hashes, refuse symlink ancestry and each
destination collision, and prove forbidden profiles refuse before transport.
Existing D112 tests remain the oracle for capture and callback semantics.

No new material wrapper API gap is apparent. The draft's whole-image ownership
wording should include the coordinator's selected timing boundary: exclude
competing/reachable peripheral owners during and after ADC admission; audited
stock-loader RCC/PWR/DAC pin-control initialization before admission is recorded
and checked against the unchanged native guards, rather than described as absent.

Decoder/readout test authoring should wait for the promised literal public schema,
fixed artifact/layout identities, exact read regions/count/byte/time limits, and
per-category failure results. In particular, freeze whether equality compares all
bytes or only named fields: the draft both requires identical terminal snapshots
and says to ignore ABI padding. Recommended explicit interpretation is to retain
both raw images while comparing defined report/committed-capture fields for
semantic equality, excluding padding and private pointers; document any stricter
raw-identity requirement separately. No floating-input value oracle is appropriate.

The eventual independent literal fixtures should distinguish complete128 records,
truthful FAULT with its actual committed count, RUNNING/nonterminal even when two
reads match, changed defined fields, truncation, wrong deployed identity, invalid
enum/chronology/count, and nonzero padding. A positive acquisition result must
require all128 real committed captures with actual UNCONFIGURED decode evidence;
collection integrity, frozen-state evidence and physical acceptance must remain
separate. The current ABI numbers are baselines to verify from the selected ELF,
not a substitute for that verification.

This is a bounded preflight, not a full decoder review. D113 independent execution
has priority; no D114 executable expectations have been frozen or implemented.

## Coordinator selection after preflight

The coordinator chose strict full-byte equality of both terminal Runner snapshots
for the frozen label. Typed parsing still ignores padding and private pointers as
measurements. Different padding therefore means **unstable**, not malformed;
both original images and both typed observations are retained. This resolves the
equality-domain question and is a testable distinction. Exact capture API/schema,
artifact/layout pins and read ceilings remain pending, so no decoder tests follow
from this clarification alone.
