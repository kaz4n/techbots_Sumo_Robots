# Independent D086 pair supplement

Run `python3 -m unittest tests.tooling.test_adc_pair_unoq -v` under Linux/WSL.
The subclass reuses the established battery runner and executes all nine of its
methods unchanged, then six new pair methods. No established assertion or
`test_power_unoq.py` edit is required.

Expectations come from the frozen D086 contract, public power/config headers,
the pair prerequisite audit and retained installed/manual sources. Production
`.cpp` bodies are only copied, hashed and compiled; they are not read to derive
assertions. Every command retains its first result before raising on a failure.

The existing native fixture received narrow additions:

- A1/index15 maps to GPIOA/PA5; `channel_a` is channel10. Named GPIOB/C and a
  structurally identical foreign device support fixed-profile exclusion tests.
- New malformed-pair variants leave every existing malformed-battery variant
  unchanged. Existing installed constants already include SMP10 and DAC2 fields.
- Optional channel-specific values are selected using the rank captured at
  ADSTART. Default conversion data remains the existing `hw.sample` value.
- Rank-write before/after hooks, ignored/transformed writes and elapsed time
  allow independent partial-transition and deadline tests. Their defaults retain
  the previous successful-write behavior.

New cases cover ABI/status compatibility, both profiles, repeated setup refusal,
destructor inactivity, exact PCSEL/SMPR2/SQ1 setup, alternating and repeated ranks,
raw identity/limits/sequence, shared claims/faults, PA5/DAC2 ownership, final guard
time, ADRDY loss during setup, stale/partial flags, rank-write readback, bounded
cleanup and allocation-free runtime. The inherited PA4-only neutral setup remains
allowed: GPIO write traces must preserve PA5 and all unrelated fields. No DAC or
lock repair is permitted.

The sequence-wrap test seeds `button_sequence_` after an ordinary successful
conversion through the authorized private-header seam. This tests the wrap
boundary, not billions of acquisitions. The unchanged process-isolation listener
propagates child assertion/crash failures; doctest's printed assertion totals are
parent counts and do not include every assertion executed in child processes.

The actual pair probe is compiled in both macro modes, with setup and ten thousand
loops required to remain inert. Eight upload combinations must reject before
transport lookup. No new allowlist key is added by the tests.

These are controlled software tests. They do not establish live ownership,
electrical settling/carryover, ADC accuracy, START/BOTH distinction, native latency,
whole-tick schedulability, SC-AJ/F091 qualification or a physical phase gate.
