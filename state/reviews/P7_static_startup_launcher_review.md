# D155 startup launcher implementation review

25 September 2026, Asia/Dubai. Separate same-model review reusing D154/D155
design context; not fresh-context, cross-model review, native permission or a
phase gate. Reviewer owns this note and startup_private.py; no board execution.

Reviewed contract SHA256
`2bdbc3c992a050383052fc87c65cd320ad395e201dd7c0e0a8f04092e1d95044`.
First inspected, unexecuted draft SHA256
`4d5ef660fb94a51801d59da7b6c31c004f9607ce3d71e18b924e34befbdc4a7f`.
This is not the draft in commit0cdfa50b: that preserved pre-test source is
`7149bfb65fdfc96d69d102ff98fd2585ae0202d4e6b0aab6e3de0cd5aa171990`,
with the author's independent local-check improvement. Pre-guard repair source
was also preserved in fdbd3cb5. No earlier draft was represented as a passed run.

Initial source findings, all resolved before first implementation execution:

- R1 **MAJOR**, first draft startup_run.py:457-458: recorded remote evidence
  paths omitted "startup-" and disagreed with both frozen output bindings.
  Repair derives the paths from checked binding bytes (current :466).
- R2 **MAJOR**, first draft :469-480 and :512: Probe writes numbered planned
  receipts before the transport callback checks local output ownership. An
  already replaced output could therefore receive a new receipt before drift
  rejection. Current :479, :483, :491 and :524 check ownership before all four
  Probe entry points; transport retains its second check. This detects observed
  replacement, not an atomic filesystem lock against concurrent replacement.
- R3 **MAJOR**, coordinator also identified first draft :541-556: a persisted
  FAILED dictionary returned through main allowed a normal zero process exit.
  Current :555-559 raises after persisting a failed result; no retry is added.

Final reviewed/first-executed source SHA256
`6f86e64504f3776d0e841d5faf551566f20ca246ff99d893e92897e9d41629e2`.
Reviewed actual source and diff against0cdfa50b, plus pinned Probe dispatch,
board transport, D153/D154 interfaces and F166 prerequisite report shapes.
The exact six-command allowlist fixes board, capture mode and timeout. Four
Linux-file forms remain available after separate local failure; upload/capture
still recheck HEAD, committed scope, pins, source/stage and ADB before transport.
Old D144 Claim/FileRecords provide packet identity, not a reused grant.

Payload framing/total hash and every module hash precede module execution;
the existing loader parser is descriptor-read/hash-checked before loading.
Windows command sizing includes the real ADB path, quoting, UTF16 terminator
and 30000-unit limit before claim. Actual native scope/current HEAD admission
is still required. No install, compile, extra reset or recovery path was found.

Upload uncertainty or any intermediate failure suppresses capture. Exact report
identities, counts, read descriptions, wait and shallow analysis are checked;
fault/no-progress remains separate from collection completion. All four final
checks run independently; prerequisite inventories and local checks retain
their additional failures. Claims/results are exclusive and file-fsynced,
numbered transport receipts are retained and flushed before successful finish.

Verified first public receipt launcher_first.json: **30/30 PASS**, exit0,
0.046s. Public tests SHA913679cfe08186240342b40d32a174bfdba93ac83fe6dccd002f2bc9edf6f68e.
Verified launcher_private_first.json: **10/10 PASS**, exit0, 0.119s.
Reviewer supplement SHA39c5f6a8ef2d620edebced2985d8d44236d51e53212860d66f73d7268280b026
was authored after source inspection; it is not an independent spec-only oracle.
It exercises actual scope/HEAD validators, transport admission, pre-receipt
ownership checks, prerequisite independence/pins, exact evidence paths and
lost-dispatch/failure propagation through controlled seams.
Both freeze timestamps precede execution; freeze hashes match their receipts.
All12 union frozen input hashes were independently rechecked and match.

Reviewed local-only launcher_composition.json, SHA7e905bf18c94e4e0d137cd2f726e4fce7f3967d09f890b24edc870c1553b9cdd:
PASS, zero Probe dispatches,16 fixed/17 runner pins,102 staged files,26 installed
pins and six allowed forms. Actual upload/capture commands are28068/24981 UTF16
units. Its source_file_count=null is an absent stage-receipt field projection,
not a measured source count; the separately checked working manifest has103
files/file_count. Preserve the raw null and this projection limitation.

**Disposition: PASS for scoped D155 host implementation; no open material
finding.** Original source findings are retained above, not negative test runs.
These tests mock processes and relevant filesystem/Git seams. They do not prove
live Windows/ADB behavior, native CLI initialization purity, MCU progress,
quiescence, timing, physical acceptance or a phase gate. A separately committed
source-bound inert run scope and fresh admission remain necessary.
