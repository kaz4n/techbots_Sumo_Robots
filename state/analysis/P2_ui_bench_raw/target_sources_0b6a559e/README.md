# A1 raw and decoder evidence bench (P2 B6 preparation)

The checked-in ADC grant is false. Construction, setup and loop make no clock
or ADC calls. An explicitly enabled future revision uses one existing Reader's
fixed A0/A1 setup profile and reads A1 only. It never samples battery voltage or
creates another ADC owner. No motor, matrix, Runtime or transport owner is used.
MATCH and uploads are refused by the checked compile route.

Compile only with the existing board connection settings:

```
python tools/board_tool.py flash bench/ui --compile-only
python tools/board_tool.py flash bench/ui --compile-only --startup immediate
```

The finite capture retains the first128 admitted raw readings at the existing
1ms cadence, with native status, source times, sequence, actual decoder output,
wrapper timing and missed releases. Each due poll makes one native read. No
filtering, voltage conversion, catch-up burst or overwritten record is used.
Failed closing time hides the tentative slot while preserving older records.

Raw-source capture acceptance is separate from button interpretation. The
production windows remain unconfigured. UNCONFIGURED, UNKNOWN, AMBIGUOUS and
INVALID decoder results remain visible; they do not synthesize a release or
prove that START and BOTH are electrically distinct. A failed A timestamp
suppresses decoder delivery, and decode_matches_sample marks the retained older
decoder output as historical. Native failures keep their real shutdown result.
The Reader has no public stop API: terminal silence does not prove ADC shutdown.

This short raw capture prepares electrical characterization. Full B6 also needs
supported windows and circuit behavior, live long-held gestures, mode/menu/
countdown display composition and optical acceptance. Existing logical/display
components remain the source of those semantics. Later capture runs require
verified source/deployment identity, ADC ownership, labelled physical stimuli
and a reviewed retrieval method. Host tests and compilation prove no physical
button levels, full application timing or phase gate. See
state/analysis/P2_ui_bench_contract.md for the exact software contract.
