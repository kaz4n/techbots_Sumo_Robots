# Independent D085 native tests

The author derived assertions from `P2_qtr_native_contract.md`, the public headers,
the source audit and saved installed headers. Production `.cpp` bodies were not
read; the runner copies, hashes, compiles and links them opaquely. The runtime
links the actual `line_qtr.cpp`; pipeline/probe cases additionally link the actual
adapter and complete pure core.

Run under Linux/WSL:

```
python3 -m unittest tests.tooling.test_qtr_native -v
```

`extract_bits.py` copies 3431 CMSIS constants, four register layouts and eight
selected LL getter bodies from the cached installed headers. Four-byte observable
words retain register offsets at the actual native addresses. The EXTI conditional
for available lines is preserved, including the real multi-bit lock semantics.
Zephyr device/GPIO declarations preserve the named fields, argument types, flags
and checked operations this source consumes; they model the consumed API subset,
not the complete Zephyr binary ABI. Actual target compilation remains necessary.
The Arduino `bit(b)` macro is retained to expose source naming collisions.

GPIO effects deliberately match neutral input/no pull/push-pull/low speed and
HIGH preload before output, with unchanged AFR and ODR on input. Native statuses,
effects, physical levels, clocks and ownership are separately injectable. Direct
register writes, forbidden setters and pad reads with disabled clocks are counted.

Each ownership scenario runs in a child process; there is no production reset
backdoor. The assertion listener reports child failures through exit status and
reports the successful child assertion count through a pipe. Two deliberate
failure/crash sentinels prove parent failure propagation. Doctest's ordinary
parent counts and these isolated child counts are reported separately.

Coverage includes metadata/ownership, every partial setup/charge/release failure,
cleanup eligibility/status/readback, exact call/charge/cleanup/frame deadlines,
final-guard elapsed cost, frozen/reversed/wrapped clocks, last-advance completion,
all sixteen raw patterns, per-pad timing bounds, late LOW and censored timeout,
generation/replay, actual adapter/Robot continuation and ambiguous 600us gaps.
The sequence-wrap case seeds the known private generation field after an ordinary
completed frame. It verifies the wrap transition, not billions of observed frames.

The pure tests separately cover malformed/ambiguous qualification, Robot source
age/identity/mode, confirmation count three, opponent freshness, retained white at
GO, escape replan/exit rules, countdown source windows and expired pivot warning
history. Runtime allocation guards include actual native/adapter/Robot construction,
three acquired frames and ten thousand duplicate transactions. Both probe macro
modes leave constructors/setup/ten thousand loops inert; eight upload combinations
must fail before any transport lookup.

Receipts under `state/analysis/P2_qtr_native_raw/author/` preserve command arguments,
status, normalized stdout/stderr and source hashes, including initial failures.
No test contacts a board or proves physical cadence, discharge precision, pad
handoff, debugger absence, electrical behavior, whole-tick WCET or a phase gate.
