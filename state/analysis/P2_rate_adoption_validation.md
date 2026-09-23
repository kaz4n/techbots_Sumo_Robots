# D-072 production logging-rate adoption — 2026-09-23

IMPLEMENTED/HOST-TESTED/TARGET-COMPILED/REVIEWED development change. LOG_HZ25
is the single changed B16 value; other75 defaults,200s window,4096events,1kHz
control and every motion/sensor parameter remain. Config/spec document original50
and actual RAM reason explicitly. D-072 contract1dd1050 preceded edits/tests.
Original phase/hardware/motor gates remain pending.

## Changes and independent expectations

Current production source gives5001 frame endpoints at40ms cadence,130026B
stored-frame payload plus32768B events=162794B. No core/HAL body or locked file
changed. Existing unlocked tests retain every case/assertion purpose and multiple
wraps, interior/newest alias, status/loss/event independence and fixed-seed streams.
Three-skipped-slot scenario now checks80/120/160ms; current-yaw case accounts for
GO5100ms being20ms off the40ms recording phase. Six previously independent D-071
candidate cases are promoted into the normal suite; their historical source stays.

Recorder experiment builder accepts current25 or historical50 literal source and
both destinations, changing only the two copied rate digits. Exact source rate,
bytes and manifests are recorded. Conditional/spliced/ambiguous declarations fail
before copying; compiler failures still propagate. No new upload option/authority.
Actual repository25 source prepared both25/50 copies successfully without board
calls, recorded in live_candidate_preparation.json.

## Actual checks

- Full normal975cases/15667813assertions pass,0fail/skip,2.677s after one fixture
  include repair. ASan/UBSan same975/15667813 pass16.623s. Locked10000Robot streams
  and other fixed-seed requirements preserved. The lower total assertion count
  follows actual ring capacity in full/wrap checks; no case/assertion was removed.
- Focused builder/probe21 tests pass initially; after reviewer ambiguity findings,
  independent red regressions and first repair,23pass3.525s. Fresh reviewer
  reproduced23pass2.845s and975host cases. All original fixture assertions retained.
- Full tooling338 pass134.754s before parser repair. Final-source whole-tooling
 340pass140.157s, exit0; wrapper elapsed146.009s. The final receipt is retained
 in P2_rate_validation_raw/all_tool_tests_final.* and independently reviewed.
- source_comparison.json: onlyconfig changes among43 previously protected files;
  sole declaration value changeLOG_HZ50->25. Compared to D-071 candidate25, the
  actual30-file staged source differs only in config comments, non-comment tokens
  identical. No hidden sensor/control or body change.

Actual UNO Q Linux default/MATCH0/MOTORS_ALLOWED0 compile exits0. Source SHA
772bda5578ef4be55513b95e25d433a225faeadefdf4c6efb119457f3140c690; image294932B,
compiler RAM226584B, difference35560B. New remote ELF SHA
b1fd86780b5d2a3a91c7c41031a2329484226991f5a198309bc8515d60a3df76 equals the
reviewed committed D-071 candidate ELF exactly. Existing ABI/section/constructor/
reset-stack inspection therefore applies to these identical artifact bytes.
No upload/reset/MCU call, peripheral operation or motor run occurred.

Five existing inert source guards were independently approved/refreshed exactly:
matrixd847e739,timing78c396b9,ADC83b33e9e,GPIO22861454,QTRcf841b58. Full hashes/maps
in P2_rate_inert_manifest_proposal.json. No keys, startup exception or upload path
added. A guard refresh does not mean any image was uploaded.

Failure/history: P2_rate_failure_analysis.md and raw receipts retain initial missing
include, reviewer MINOR/red/first repair and small WSL clock-skew warnings. Raw
receipt bytes are binary-preserved. Fresh read-only same-model review is separate
from implementation/spec-only author and is not cross-model or a human gate.

## Remaining qualification

SC-AH's source-rate selection is resolved; deployment acceptance is not. This
memory-probe compile omits later HAL/application integration, and no actual load,
free-RAM/fragmentation,200s/no-gap dump or full worst-case tick was measured.
Conditional loader230072B peak/largestallocatable32068B remains source modeling.
Inherited Bridge mutex waits/initializers (F-091), include macro boundary and
2392B reset local stack before callees remain. No physical/gate acceptance follows.

Next eligible preparation: audit B15 dump fields/recorder public interfaces and
existing dump tool, then specify a bounded offline readout/serialization contract
within B8. Do not introduce Bridge calls, actual dump requests or app integration
without their separate runtime/phase requirements. Preserve all earlier evidence.
