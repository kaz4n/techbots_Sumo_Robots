# D202 compile-time motor metadata derivation

26 September 2026. Proposed narrow engineering scope under D051, following D201
fault localization. Adoption is recorded separately in DECISIONS.md before
implementation. This contract does not authorize an upload or assert a timing
repair.

## Evidence and objective

D201's saved lifetime SETTLE failure is FINAL_DEADLINE,154us,poll5,fresh7;
initialization failed. This identifies a rejection predicate, not its physical
cause. D199's accepted file-entry result `10d8a184` contains runtime unsigned
64-bit division dispatches in candidateRate and candidatePeriod. These compute
expected values solely from fixed DT/config metadata. Eliminate those runtime
calculations while retaining every live observation and safety decision.

Predecessor: src/hal/motor_port_unoq.cpp,19185 bytes, SHA256
f1ee755a7bddec38e86545f4c5e5457b3ed5e5f1bdd7f5cf368cc77f91664f5e.
Retrieve its exact bytes from committed D201 HEAD
ff35c83e6d21d299dac14eb6fc5570d173a7772d; do not alter the historical source or
evidence. All configuration, headers, locked tests and diagnostic report remain
unchanged.

## Only permitted production edit

Replace the two calculation definitions from candidateRate through
candidatePeriod, ending immediately before pinMask. All bytes outside that
region remain exact. Introduce constexpr expectedRate and expectedPeriod:
their calculation bodies are the original bodies, with only function-name
substitution and expectedPeriod calling expectedRate. Preserve integer widths,
casts, conditions, short-circuit order, arithmetic and zero returns.

Retain the original candidateRate/candidatePeriod runtime names and signatures.
Each selects among three automatic constexpr scalar results, initialized by
the corresponding derivation helper with literal indices0,1,2. Invalid indices
return zero. Use clear if/return or switch selection. No table, new persistent
storage, constructor, runtime guard, mutable cache, device access or allocation.
The constexpr initializers require evaluation at compile time. Do not merely
mark a variable-index runtime calculation constexpr and assume it was folded.

Preserve these predicates exactly: invalid timer/PSC/domain/selector; nonzero
HCLK/AHB/APB; APB power-of-two and <=16; HCLK/APB divisibility; HCLK already being
HCLK; the existing APB kernel multiplier; 64-bit PSC+1; exact kernel/divider and
rate/carrier divisibility; nonzero carrier/rate; period1..65536. No replacement
literal rates or periods, purchased library, pin or wiring assumption is allowed.
Existing PRESCALERS/DOMAINS/SELECTORS declarations remain byte-exact. Whole-Port
zeroing when any selected channel is unsupported remains unchanged.

No other production region changes. In particular, retain settle's exact body,
150us/4096 bounds, unsigned timing, existing micros calls, stale clears, fresh
bits, per-poll bank check, EN LOW/readiness/ownership, timer register reads,
PWM getter observations, native call order/count and activation checks. Do not
cache any live state or claim a timing gain before target evidence exists.

## Independent host evidence

Freeze a separate oracle before implementation review/execution. The author
may inspect only this contract, the pinned predecessor and unchanged fixtures.
The implementer must not author or alter that oracle.

1. Check exact predecessor pin and outside-region equality. Independently check
   the unchanged derivation bodies, forced constant-expression initializers,
   original runtime signatures and zero behavior for invalid indices. Confirm
   no new state, initializer or diagnostic exposure.
2. Compare predecessor/current probe0/probe1 across all21 existing native
   diagnostic scenarios. Preserve complete ordered API/clock transcripts and
   final fixture state, source-predicate reports, immutable settle body and
   layout. Direct MMIO statements are protected by byte-exact unchanged regions.
3. Query candidateRate/candidatePeriod in same-translation-unit host fixtures;
   no production test seam. Independently calculate expected results and compare
   predecessor/current for indices0,1,2,3,UINT32_MAX. Cover valid APB1/APB2
   divisors1,2,4,8,16; varied valid HCLK and PSC; zero/nonintegral/invalid
   metadata, wrong domains/selectors/encoded divisor, period endpoints and
   out-of-range periods. Include isolated invalid-timer metadata and verify
   whole-Port zeroing. Preserve all64-bit arithmetic and invalid conditions.
4. Additional fixture macros or alternate config values must live only in new
   unlocked, isolated fixture files or exact recorded temporary projections.
   Never edit the locked fake DT/header/cases or real config. Feed identical
   metadata to predecessor/current. No hardware, subprocess transport or motion.
5. Run the existing locked native suites unchanged, serially. Run the unchanged
   D197 diagnostic oracle as well: its settle-body and native transcript checks
   remain applicable. Preserve any whole-symbol inventory difference; do not
   filter its assertion, add artificial used attributes/references, or erase
   failures. A symbol difference needs explicit review before further action;
   no assumption of a pass is permitted. The historical test remains intact.

Run with Python-B, bounded serial compilers, immutable input pins and exclusive
evidence owners. Keep first failures and compact outputs before releasing owned
temporary objects/executables. No retry of consumed native owners follows.

## Review and target boundary

D202 supersedes D197's production-helper immutability only for this exact
metadata-calculation region; it preserves D197's report and all native safety
semantics. A separate reviewer checks the scoped patch and independent results.
Only after host validation and review may a new fixed compile-only workflow be
prepared. New checked artifacts and actual ABI/entry emission are required
before any separately reviewed inhibited runtime attempt. Verify that runtime
division dispatches are absent from the new candidate helpers, and inspect any
storage/code-size differences. Host equivalence and removed instructions alone
prove neither duration, WCET, reliability, physical outputs nor a human gate.
