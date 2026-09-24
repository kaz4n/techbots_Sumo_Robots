# Proposed P5 abort evidence: scoped design review

Reviewed original revised proposal SHA256 `00e8f150287bfb94c02bcd8eb41db43d2ea279280fe60abaee8f89bff413ea6c`, then final proposal `c6314c0439b1cd992c42f39aee0638225998ffae18a364f3638662098c63d0b2`, options, existing-test map and relevant current owner paths.
Separate-context same-model reviewer with reused P4/D134 context; not cross-model review. Proposal remains unadopted. No implementation/test edits, compiler or board execution.

- **MAJOR, CLOSED — `state/analysis/P5_abort_evidence_contract.md:167`:** final text makes EN=true a mandatory M1 producer condition for ABORT_APPLIED and requires INVALID_RECEIPT for EN=false. The earlier physical-qualification-only wording was insufficient because wire records omit EN. Independent receipt tests must include this explicit negative condition.
- **MAJOR, CLOSED — `state/analysis/P5_abort_evidence_contract.md:306`:** final text restricts offline validation to serialized Rs/Re/D/A, ordinal grammar and metadata, while explicitly identifying omitted T/C/next-T, full-token and EN claims as producer-enforced/source-bound. It no longer promises independent reconstruction of absent fields.

The revised Pending reuse is sound as specified: source admission checks Rs/Re against the same T/D subsequently captured in tagged Pending; receipt validation extends that common-anchor order to A/C/next T/next D. The attempt RECEIPT phase and tag must both match before success, and receive closes them before clearing/replacing Pending. Full64 token matching, reset/exhaustion handling and no-later-repair rules retain identity without another persistent timestamp/token owner.

The cause/phase table matches actual B12 predicates: SIDESTEP PIVOT front-plus-outer is a side cause but may route TRACK; ARC PIVOT ignores detections; WAIT widening starts a flank rather than an abort. Phase advancement within a call, snapshot-only and natural completion are distinguished. Predicate capture and actual route observation remain separate; absent predicates still require independent behavior tests.

The logical metric is honestly limited: same-observation handover plus conservative A-D<=TICK_US, with actual late values retained. It does not timestamp physical appearance or prove PWM/mechanical response. Source/edge/STOP priority, previous-receipt-before-current-preemption ordering, terminal prefixes, missing tails and one-candidate ownership avoid favorable retries.

Keeping P5 EventBatch21 avoids the prior capacity growth. Explicit prefix retention, all attempted appends, existing loss counters and whole-attempt disqualification make overflow nonqualifying even if a visible success suffix survives. Representative loss-free and saturated negative cases remain required; D129 capacity26 and its grammar stay unchanged.

**Deployment limitation:** historical default modeled headroom16 bytes is not a budget for the new profile. Conditional pulses/input copies/tag/phase, native code/loader, stack and actual full-tick cost can still exceed it. Lines280-290 correctly retain target realization as unresolved and forbid silent B15/B16/openers tradeoffs. Empty-grant M0 fit cannot establish a later M1 artifact's fit or run authority.

**Draft disposition: PASS for the proposed bounded software-preparation design; no open BLOCKER/MAJOR/MINOR.** Proposal remains unadopted. This is not implementation acceptance, target readiness, physical10/10 evidence or a P5 gate.
