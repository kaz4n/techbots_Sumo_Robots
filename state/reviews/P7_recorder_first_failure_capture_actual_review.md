# D233 actual passive first-failure capture review

FINAL PASS for the saved passive observation, provenance and closure. No open
material evidence finding. The delivery remains FAILED. Reviewed2026-09-27
using retained local evidence and pure recomputation only; no test, native
command or source change was performed. Only this review file was written.

## Bound image and evidence

Collector HEAD: `3c9f11f5cc9550e1423a5cca01bf274c33f7da22`.
Native compile HEAD: `ce4e69390d21d9a91231581a186be4a63213135e`.
Attempt: `07f19e32c483cebadecaa63f4d6d720f`.
Expected session: `572412568535289530`.
Source: `29cb1e76193e4b7c562d1fd842039f61367a82c2651a2303c09518d35a0c7ce9`.
Owner: `state/analysis/P7_recorder_first_failure_raw/native_capture01`.
Remote owner ends `/recorder-07f19e32c483ceba-failure-capture01`.

All172 input hashes independently match:171 relative inputs match exact
collector Git blobs and current bytes; the external ADB binary matches its
pin. They include all145 historical compile input hashes. Both capability
observations are identical and their110 source hashes equal the complete
staged recorder inventory, using the /recorder mapping. They bind boot
55c386b9-fe6d-4388-a7f4-1d91e0bb49d8, UID1000, no-bytecode execution and the
exact adapter/source identities. Target serial remains2629958581.

Recomputed the spec from accepted ABI
`221717e2f45fa51a63a82def322e3c287047d9565b207ae1463142d674c0c7c2`.
Its canonical SHA-256 is
`defe61a6562422753bde9e15ea7465a1d02aa9476ae3750042cc9fd3d7f9c120`.
The source-derived243780-byte adapter exactly equals the staged bytes/hash
`1fea17af0f33972f98b058653e7ddda01c09d552edea2ed1c2427440806ee5cc`.
The scope hash is
`7077ea3be007fac70a6b7dae6c5a474030fd6f2d52d1bc5face13cdb1766bcaf`.

| Saved file | Bytes | SHA-256 |
| --- | ---: | --- |
| `inputs.json` | 19654 | `6c1d98b445ea47215f5b5344690c2658a71c55cd288306aa61c8513359d85972` |
| `capture_result.json` | 11809 | `a1641460b6fc99655f7a66a75f908d2e40555a26d7763d6e2e3d0a0c02bd53bd` |
| `result.json` | 78434 | `dbce1db9ae0838bbdc1c32a36aa95e593ebad5b3427948df7f125541ced8a27d` |
| `export.json` | 8858 | `afbe77787d75e1cef2f6b26ef198992ec933cf903e47a4ac6a03950bed61258b` |
| `final_checks.json` | 57077 | `a8eb1eec8230c210ee8c3184eba00dd4685cebaf889ea2d50037a01dc19645a4` |
| `root_actual_closure01.json` | 1173 | `cf73eeda8b5f850f65095b99a28520903bb6c552089a21247635440529776a1a` |

## Actual collection and closure

One capture and one read-only retrieval completed through exactly10 bounded
transports. All intent/result pairs agree, return zero and retain empty stderr.
The action counts are one adapter claim/push, two prerequisite initialization,
two built-in inventories, two capabilities, one capture and one retrieval.
Staging is claimed/verified/ready; no retry or second capture is recorded.
Both result and final_checks have matching diagnostics and empty local,
prerequisite, finish and transport error lists. All44 saved local Git commands
return zero with empty stderr. Overall status is COMPLETED, with null first
error and no postcheck errors; export bundle_status is PASS.

The exact plan executes24 passive reads totaling639496 requested bytes. Full
263680-byte loader and55376-byte sketch comparisons pass before any SRAM and
again after both snapshots. The two whole-sketch hashes independently equal
the compiled package b13a32b5e92993a49f165b907d5d6036fa933e1680bb23ff2738620b294fd584.
Every before/after flash chunk hash agrees. Full flash bytes remain in the
durable remote owner; local evidence contains their checked read hashes and
the native byte-comparison results, not another full flash copy.

Each snapshot covers the six fresh ABI ranges totaling692 bytes. The native
observation interval is21:39:51.962102 to21:43:06.400488 UTC on2026-09-26,
after the delivery receiver's21:37:22.553842 terminal closure. The two-second
sample separation records2.000391599 seconds. Exact read count, addresses,
extents, ordering and timing brackets pass the reviewed reply validator.

Retrieval returns the durable report plus all12 status files. All13 closing
file checks pass with identical expected board identity before/after. Decoded
base64 bytes, sizes and hashes match the returned rows, saved files and read
report. The returned capture envelope canonicalizes exactly to its saved
counterpart, and its report hash/bytes bind capture_result.json. Independently
decoding all raw statuses reproduces the complete remote analysis and local
export. No decode error exists; all64 paired fields agree. Coherence remains
UNPROVEN: equal sequential samples do not establish an atomic snapshot.

## Recorded first failure and limits

Both samples retain these first-failure fields:

| Field | Observed value |
| --- | --- |
| reason / site | TIMEOUT(9) / STORE_DEADLINE(13) |
| packet offset / packet size / payload size | 7 / 74 / 59 |
| cleanup | READBACK_FAILED(5) |
| cleanup ownership / evaluated | OK(1) / true |

The eight raw record bytes are `09 0d 05 01 07 4a 3b 01`. The16-byte windows
07-first.1.bin and13-second.1.bin both hash to
`77fcf8f52e9c697cf50a0842602b8e67046707f3b3197023dc46048efd287e5e`.
Current native status is POISONED; initialized/attempted/poisoned are true,
active and cleanup_verified are false. The preserved first record therefore
supplies the earlier reason/site that the current poisoned status alone lacks.

The source-bound STORE_DEADLINE site is the withinDeadline check immediately
before a subsequent TDR store. That predicate combines the per-step and
per-packet limits. No failed-predicate branch, clock operands or interrupt
latency is retained, so this observation cannot select which limit expired.
Offset7 is software packet progress. It does not prove seven shifted bytes,
seven receiver bytes, any complete envelope or acknowledged payload.

READBACK_FAILED with ownershipOK/evaluatedtrue records the source's failed
CR1==0 cleanup verification after its inhibit attempt. The snapshot contains
neither the failing register value nor evidence of why it differed; no readback
mechanism, competing writer or peripheral timing cause is inferred.

Other paired fields record RunnerFAILED/DUMP after202479 epochs, dump setupOK,
missed releases0, maximum recorded execution482us/lateness2us, and zero enabled
EN/nonzero PWM/invalid motor calls. Transfer is FAILED/PORT with bytes, frames
and events all0. Runner and transfer sessions match572412568535289530.
These are observed reports, not physical motor evidence or qualified WCET.

The compact root closure agrees with the fields and counts. Its phrase
"after7submittedbytes" is bounded here to the recorded software packet offset;
delivery remains unproved. This capture identifies the retained native failure
site, not its ultimate cause or a repair. It permits no new upload, reset,
grant/ready-pin change, motor run, physical acceptance or phase gate.
