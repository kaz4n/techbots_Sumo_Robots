# D105 independent test scope

The author has prior D104 C++ probe context, but did not read D105 production
implementation bodies. Expectations come from the adopted delivery contract,
public Runtime/calibration headers and existing public test fixtures. Source
files are copied and hashed opaquely for isolated builds. No private production
state is seeded and no established or locked test is edited.

Parser tests froze first: ten methods cover literal canonical syntax, exact
types, all timeout/value bounds, passive import/pure repeatability, file-only CLI,
exact snippet and five-field JSON publication, unmodified production config,
malformed/oversize/extra bytes, directories, missing files, existing outputs,
symlinks, FIFO refusal and required explicit timeout. Linux/WSL first author run
passed all ten, with no skips or oracle corrections. Exact receipts are in
parser_freeze.json and parser_run1.json/txt.

Runtime tests froze before any D105 implementation build/run: 26 C++ cases use
actual eight-request calibrations with real Robot/Gate receipts and owner banks.
Coverage includes grant/MATCH truth, exact output and parser roundtrip, successful
second banks, no delayed retry after refusal/menu re-entry, PENDING and partial
byte acknowledgement, identical pending offers, early-call passivity, permitted
raw ABSENT frames, missing ports/failed setup, invalid write responses, poisoned
readiness, failed receipts/sources, new capture cancellation, complete S..C
callback timing, clock regressions, exact freshness boundary, actual STOP and
service-only reset, explicit abort after motor halt, stall, isolated total
deadline, natural wrap and both directions of real recorder arbitration.

The harness tests non-MATCH and MATCH in normal and ASan/UBSan builds. Synthetic
button windows are applied only to temporary copied configuration. A separate
isolated 20 ms stall/40 ms total profile exercises TOTAL with one acknowledged
byte every three epochs; production thresholds remain unchanged. A default
300 s total deadline is not claimed reached by the short snippet fixture.

Review-only limits: the public actual Runtime cannot independently inject token
skips or same-token changed timestamps, mutate a committed bank without changing
its version, exhaust uint32 versions, fail formatting of a genuinely valid bank
within the required fixed buffer, or withdraw copied callbacks mid-attempt.
These are not simulated through private mutation. Early-call duplicates and
actual post-STOP service-only non-retry are tested, but no claim is made of
forcing an otherwise unreachable retained committed=true owner state. Parser
file-read-size enforcement requires source review; black-box CLI tests establish
rejection/publication boundaries, not the exact internal read call size.

No board/network operation, shared build, upload, commit, physical calibration,
UART acknowledgement, motor action or human gate is performed by these tests.
