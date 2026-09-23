# D112 UI bench independent test preflight

2026-09-24 Asia/Dubai. Reviewed the full draft, declaration headers, public
power.h/ui.h/power_inputs.h/types.h/config, and D086/D087 contracts. No native,
decoder or future Runner implementation body was read. This reuses the separate
D104-D111 author context and same model, not fresh repository or cross-model
review. Only this preflight is authored; no executable test, production, config,
registry, shared ledger, hardware action or gate is changed.

Reviewed draft SHA256:
`7dc75a8e2239664924bcfeb7659ba49e1198fbb363e21d8e3a94d3580b7788c9`.
Public Runner header: `6a6a26832842abe8e3df857216f31c799cd76de18b37dd1701e3d5714735190a`.
Public Native header: `d28d53b8104a5927b648b2e008c1eea21bb4aeafa3020149a9e939d8396391ae`.

## Result

PASS for independent oracle readiness. No concrete missing outcome or material
source-age/decoder-precedence ambiguity was identified. The draft distinguishes
raw-source capture acceptance from logical button qualification and permits
meaningful public-only tests without an additional seam or private state seeding.
Adoption is still the coordinator's next action; this review does not adopt it.

## Observable interpretations checked

- Disabled grant precedes callback/config validation. Enabled setup classifies
  actual known provider failure before A chronology, preserving setup first cause
  and independently recording a later clock fault. Setup timing is S..C.
- A due read first clears only its actual-attempt flags/timing validity, retains
  its returned raw Sample and sets sample_seen before A. Semantic raw classification
  wins before A chronology; the A clock may already have been obtained. Rejected A
  preserves the older decoded object and sets decode_matches_sample=false.
- Chronologically admitted A always delivers the returned Sample to the actual
  decoder, including ADC/CONTRACT failure paths. The decoder's complete actual
  result is retained before source admission and C. It never changes the wrapper's
  first cause, supplies source validity or grants a successful capture.
- Canonical default ButtonSample returned by an actual read is a particularly
  useful distinct case: the wrapper rejects NOT_INITIALIZED as ADC, while the
  actual D087 decoder can report canonical ABSENT. This must not be replaced by
  an invented INVALID decode. Before any read, the declared default ButtonDecode
  is historical non-execution, including default explicit_values=false.
- Admitted raw conversions may publish actual UNCONFIGURED, UNKNOWN, AMBIGUOUS or
  decoder-config INVALID evidence. NONE with INVALID presence is not release.
  Synthetic window/age profiles can check these paths without changing production
  windows or placing Robot/gesture semantics in this bench.
- Raw shape and source interval checks are distinct. Native failures retain real
  diagnostics without success-only timestamp rules; successful duration equality
  is SOURCE_ORDER after admitted A and actual decode. A decoder rejection caused
  by that duration may coexist with the wrapper source fault without replacing it.
- Cadence age anchors to the last committed sample.start, accumulates through all
  accepted clocks and early polls, and reanchors only after healthy C. A late C
  can make the next read due but adds no skip count to the just-finished read.
  Due-read missed count is determined at S and survives later semantic/A/C failure.
- Old source-era age remains authoritative until C, including a rejected A/C that
  would otherwise appear to renew it. Aggregate half-range rejection prevents
  small consecutive deltas from reviving stale modulo evidence. Before first
  capture there is no prior-source era, only wrapper chronology/bracket checks.
- An early or bad-S poll preserves historical read timing and sample/decode flags;
  a real read clears last_read_accepted/decode_matches_sample. Bad C retains its
  already-returned sample and actual decode while hiding only the tentative slot.
  Prior records never change. Terminal polls clear fresh and otherwise stay passive.
- No public stop/cancel exists. Completion or failure cannot fabricate cleanup,
  a disabled ADC, a new owner, or FAULT_LATCHED through an extra read.

## Reachable independent tests after adoption

Use fixed public-clock/provider fixtures for grant, callback, setup/raw enum and
shape matrices; exact cadence/skip boundaries; S/A/C chronology and aggregate
source age; source duration and first/duplicate/gapped sequence; successful final
and failed partial capture; retained read/decode provenance and timing. Default,
one and zero capacity plus strict zero/half-period profiles are directly reachable.
Natural timestamp wrap needs no private seam.

Link actual ui::decodeButtons and compare every stored ButtonDecode member against
that body on the exact independently constructed ButtonSample; add D087-derived
synthetic window endpoint/overlap/unknown/unconfigured/malformed-config expectations.
Pure output equality alone cannot prove the decoder was called exactly once;
that structural count requires source review alongside executed diagnostic paths.
There is no reason to add an injected decoder callback for this purpose.

The proposed TICK_US=conversion=1 profile publicly reaches missed-release exact
UINT32_MAX and then attempted overflow with five captures. Consecutive source ages
half-1, half-1, 4, 2 give local skips half-2, half-2, 3, 1; each successful C
starts a new era, so it does not violate the aggregate-age bound. This is a
synthetic arithmetic test, not a physical one-microsecond conversion claim.
Other huge diagnostic counter branches remain source-reviewed if not executable
within sensible finite bounds. First native sequence1 cannot reach wrap in128
captures; no private sequence seed or impossible coverage claim is appropriate.

Counted definitions of the existing Reader methods can execute the actual future
Native binding and sketch. Check zero initial clock/native counts, scoped
constructor/port/destructor passivity, one owner identity, exact forwarding,
beginWithButtons/readButtons only, forbidden legacy begin/read calls, heap silence,
and default setup/10000 loops. This verifies binding selection, not actual ADC
register guards, settling or hardware freshness; existing native tests retain that
separate scope. Target/policy/ELF/loader review remains coordinator-owned.

Physical A1 windows, START/BOTH ambiguity, stimuli, clock accuracy, acquisition
timing, long-held gestures/display composition, ADC permission and phase gates
remain unestablished. No executable test authoring has begun for D112.
