# D109 independent test preflight

Draft scenarios only, before coordinator adoption and before implementation.
No new test source has been created or production implementation read. Basis:
P2_qtr_raw_contract_draft.md, the two bench public headers, line_qtr.h,
line_qtr_adapter.h, and the D085/D089 contracts. Prior D104-D108 context is
retained; future tests are independent of the new D109 implementation bodies,
not fresh whole-repository or cross-model review.

Observable questions sent to the coordinator: truthful NOT_DUE timing at S and
a straddling S..A bracket; the exact point at which coherent neutral evidence
clears cancellation uncertainty; primary-fault ordering before A chronology;
timing last_valid/measurement behavior after a rejected S or C; active-stop
ordering among malformed cleanup, changed identity, explicit unsuccessful
cleanup, wrong cancellation status and bad wrapper chronology; and preserving
the existing Reader's responsibility for pending-frame acquisition guards.

Planned independent fixtures use literal structurally valid IDLE, CHARGING,
DISCHARGING, finite-LOW COMPLETE, mixed LOW/right-censored COMPLETE and provider
FAULT records. Each fixture's expected raw qualification will be checked with
the actual shared validateRaw implementation compiled opaquely, without changing
that validator. Frame interval math follows D085: lower is max(0,H-Rafter-1),
exclusive upper is L-Rbefore+1, timeout preserves its actual lower bound and
has no finite upper/LOW timestamp. Cleanup is a separately retained literal
record. No color threshold or scalar-discharge substitution is used.

Planned groups after adoption:

- Constructor, default/disabled/prebegin/terminal silence, one-attempt begin,
  copied callbacks, every missing callback, and enabled zero-capacity refusal.
- Exact begin/start/report/advance/cancel call order; no extra report after an
  advance/cancel return; valid and invalid command/phase combinations; immutable
  NOT_DUE records and its first-start/timing boundaries.
- First sequence 1, contiguous identity, unchanged active source identity,
  exactly one advance increment, source brackets/spacing/nonoverlap, actual
  uint32 time wrap, aggregate active-operation and source-era half-range guards.
- Complete raw validation through the actual shared validator, every array and
  status field retained, invalid/provider distinction, one append per accepted
  complete, 128 records and capacity 1, stable pointers/member values, inaccessible
  tentative slot after bad closing C, bounds including UINT32_MAX, final fresh
  pulse and later terminal silence.
- Published-record preservation through stop/fault; possibly active versus
  coherent neutral cleanup; known provider faults avoiding repeated cleanup;
  cancel-once even on failed clocks, malformed results or unsuccessful cleanup;
  independent clock_fault and retained primary/cancellation records.
- Setup S..C, command S..A, poll S..C and cancellation P..Q metrics, explicit
  callback and measured counts, last_valid history, and callback-cost accounting.
- Actual new Native binding with counted substitutes for the existing public
  Reader methods, one stable owner, passive constructor/port/destructor and
  actual default sketch silence. Compile-time forbidden flag refusals.

Normal and ASan/UBSan variants will run after the tests are frozen. Config
profiles are default capacity 128, capacity 1 and capacity 0 only. No private
state seeding, const_cast, native pin operation, transport or hardware action.
Sequence wrap is not naturally reachable in a new 128-frame Reader. Counter
saturation is similarly impractical through public finite captures, so typical
counter behavior is executed while saturation branches/callsites remain a
source-review obligation. These limits will be explicit in final evidence.
