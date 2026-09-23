# Independent authoring evidence

The author read the public D079 header/contract/config, installed-header audits,
and the previous native-power fixture infrastructure. The new production CPP
was never opened for authoring. Source bytes are staged and hashed opaquely.

Before the automatic fixture receipt runner existed, a direct fixture-only
compiler invocation failed on two fixture issues: GCC's integer-to-pointer-size
warning in the unchanged installed RCC source body, and misleading indentation
in the new write trace counter. The first was handled with a narrowly scoped
diagnostic pragma around the unchanged installed RCC body; the second by putting
the independent counter updates on their own line. A subsequent direct compile
returned exit 0. These initial command outputs are in the tool transcript; this
note is a chronology, not a fabricated raw subprocess receipt.

The first automatic fixture selftest compile failed because doctest could not
decompose an unparenthesized bitwise expression. Explicit masked comparisons
fixed the test expression. That failing compiler receipt is preserved alongside
the passing compiler/execution receipts. Assertions were not removed.

A PowerShell/Python command intended to add a test include failed at Python
parsing due to quoting; it wrote nothing. The include was added with apply_patch.

The separately authorized D079 config test extension adds exactly ten explicit
uint32 defaults and one test method while retaining strict total declaration
equality and all old assertions. Twelve local tests passed; the coordinator
also retained its independent replay and original pre-extension failure.

Fixture selftests and translation-unit compilation alone are partial evidence.
Completion of the native production suite, target compile and independent review
must be recorded separately. No software result supplies hardware qualification.

Initial actual-source SHA-256 beginning `82b0c331` passed the core transfer suite.
It then failed single-PD12 and single-PD13 lock rejection at setup and runtime,
and failed a test changing PD12 ownership during the pristine ISR observation
before the first pad write. Strict assertions and all failure receipts remain.

Two final-acceptance regressions reported by the separate fresh reviewer were
added from their test source and the public contract, without reading production
CPP. They reproduce publication of a complete 15-byte result despite a late BERR
or deadline equality during final checking. Their original failures are retained.

The initial error-evidence test expected ADDR/TCR in `error_flags`. Their status
was correctly PROTOCOL but the bits were absent. The coordinator explicitly
clarified D079 to retain causal unexpected protocol status as well as hardware
errors; the original strict assertions remain unchanged.

One synthetic pacing draft used 3000 modeled polls at every phase, exhausting
the shared poll budget before any payload byte. Production correctly returned
POLL_LIMIT; only the test's intended payload-progress assertion failed. Changing
the synthetic delay to 1000 exercises exhaustion after several bytes while
retaining the assertions of a shared budget, incomplete data and finite exit.
The original pacing failure receipt is retained.

The register model was refined to preserve each locked GPIO configuration field
when LCKK and its pin lock bit are set; separate PD12/PD13 fixture selftests pass.
This means the original setup `ready=true` observation was model behavior, while
the genuine missed admission guard is demonstrated by attempted forbidden pad
writes (and by runtime acceptance with a locked pin). The strict no-write
assertion remains. The initial receipts were not rewritten.

Repair `940f4e2c` passed error and ownership regressions. The old timing injection
selector found no register ACCESS after its third post-STOP-clear clock callback:
the new ordering added an observation. This failed REQUIRE(injected), rather than
demonstrating a new successful late transfer. The separate reviewer independently
identified the corresponding final scan after clock four. The selector alone was
changed from 3 to 4; TIMEOUT, false completion and all-zero publication assertions
were retained. Both original and repaired observations remain in receipts.
