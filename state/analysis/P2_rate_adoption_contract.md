# D-072: adopt B15's specified 25Hz fallback

2026-09-23, selected under D-051 after D-071 actual target evidence. This is an
engineering default change for recorder development, not physical tuning or a
gate. Default50Hz owner image fails356608B/262144B; isolated25Hz passes226584B.
Conditional loader230072B peak remains an unmeasured model. Complete HAL, actual
load/free RAM,200s/no-gap dump and WCET acceptance remain open.

1. Change only production LOG_HZ50->25 and matching active B15/B16 values. Keep a
   visible note of original50, B15's existing conditional fallback, D-072 and its
   evidence. All other75 B16 values,1kHz control,200s window,4096events, motor,
   sensor freshness, full hold and edge policies stay unchanged.
2. Existing capacity formula gives5001frames; frame period40000us. Preserve
   first/final endpoints, receipt matching, skipped-slot accounting, event-prefix
   overflow, reset preservation and explicit incomplete-evidence semantics.
   No core/HAL implementation or existing locked-test file may change.
3. Independent test author derives revised unlocked expectations from this
   contract/public headers/B15, never implementation .cpp. Keep every existing
   test purpose/assertion, boundary/adjacent tick, full-capacity/wrap/alias and
   fixed-seed oracle/stream requirement. Update capacity-specific literals to
   explicit5001/130026B frame payload/162794B frame+event payload and40ms samples.
   Recalculate timestamp phase relative to START, not GO (GO5100ms is20ms off
   the40ms cadence). Event4096 and motion/20ms button fixtures stay unchanged.
   Retain meaningful stress lengths where independent of ring capacity; preserve
   multiple complete wraps when recalculating capacity-indexed cases.
4. Promote the six independent D-071 candidate-only cases into the normal host
   suite under a new test file (without defining another doctest main). Preserve
   the historical candidate file/receipts. Run full host normal+ASanUBSan including
   all unchanged locked tests and required10000 fixed-seed Robot streams.
5. Keep the memory experiment builder usable for25/50 sources/destinations. Its
   public CLI/API/compile-only/safety boundary stay unchanged. Recognize exactly
   one top-level literal declaration `inline constexpr std::uint32_t LOG_HZ =
   25U;` or50U (also unsigned in controlled historical fixtures). Reject missing,
   duplicate/ambiguous, unsupported or nonliteral declarations before copying.
   Change only that declaration's two rate digits in copied config; comments and
   all original input bytes remain exact. Record source_rate_hz plus rate_hz and
   existing source/config/candidate hashes. Preserve failures and ROOT restoration.
6. Independent controlled builder tests cover all four source/destination rate
   combinations, current real-source ABI5001 capacity, unsupported/duplicate forms,
   preserved adjacent/comment content, and existing inert/macro/upload checks.
   No assertion bypass or ignore-list for changed defaults.
7. Review exactly the five existing inert source hash updates after source review;
   keys/authority stay unchanged. Fresh same-model read-only review must inspect
   actual config/spec/test/tool diffs and evidence. No upload or MCU action.
8. Stage current actual production-source memory probe and compare its per-file
   bytes against D-071 candidate25. Any changed bytes beyond documented comments
   require review; no automatic reuse of a target result for a different image.
   Target compile-only may be run if needed; it never proves load or a phase gate.

This supersedes only previous D-069/070/071 production50-retention wording for
the adopted logging rate. Original records/failed builds remain provenance.
