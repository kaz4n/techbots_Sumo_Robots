# D114 bare-board ADC diagnostic preflight

**Eligible narrow diagnostic draft, with one MINOR wording clarification before adoption.** Reviewed `49c4b0d2`; no implementation or hardware action is approved.

- D051 and the current bare-UNO-Q test instruction can support an explicit observation-only exception to D078's prior compile-only restriction. D052 itself names P0; record the new scope rather than treating prior software approval as deployment approval. SC-AJ, physical gates and pin/wiring/motor rights remain open.
- One unchanged native Reader and D112 Runner, a named true-grant wrapper and one literal four-file staging case are minimal. Preserve ordinary UI false grant/upload refusal, all old policy keys and guards; no generic include resolver or implementation fork.
- Actual native source checks both fixed A0/PA4 and A1/PA5 pads, never converts A0 here, may enable ADC1 clock before rejecting pristine state, and reasserts only already-admitted PA4 analog mode. Rank10 acquisition and UNCONFIGURED decode remain actual results. No expected floating value, successful setup or ADC shutdown is inferred.
- **MINOR:** clarify whole-image owner exclusion as competing/reachable writers during/after ADC admission. Audited stock RCC/PWR/ADC4/DAC pinctrl initialization beforehand is required; uncalled loader exports are not execution. Exact enabled-image/loader startup and worker analysis plus live ownership checks remain mandatory.
- Actual D112 debug ELF `a13d3eae` and successful ABI receipt verify Runner9892, Native32, Report132 at16, and128x76B captures at148. They are verified baselines, not future enabled-image addresses.
- Readout must preserve raw/FAULT/nonterminal/unstable evidence, ignore padding as data, and claim frozen only for consistent terminal observations. COMPLETE normally leaves ADC idle/enabled; clock-stalled RUNNING is not a successful finish.
- Before execution, freeze the decoder API/literal fixtures and exact artifact/layout/read plan with explicit read/byte/command/time bounds. P0 and D104 wrappers have different ceilings; name the selected wrapper. Require deployed identity first, immutable helper hashes, no halt/reset/write/function call, and one separately identified reviewed upload.

No tests, board or MCU operations were performed. Full source hashes, actual ABI proof and deferred obligations are in `reviewer_preflight.json`.
