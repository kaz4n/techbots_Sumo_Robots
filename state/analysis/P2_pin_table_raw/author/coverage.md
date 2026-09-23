# D106 independent test coverage

The author read the frozen D106 contract/public header and existing native test
fixtures. The author previously implemented D104's inert Runtime probe and
authored D105 tests; this is not a fresh context for the whole repository.
No D105 or D106 production implementation body was read for these test tasks.
D106 production files are copied and hashed opaquely. Compiler diagnostics may
expose source include lines. There is no cross-model independence claim.

The new test is `tests/tooling/test_native_pins.py`. It generates independent
client translation units and an installed-shaped synthetic descriptor table.
Its metadata is deliberate test data, not a hardware pin proposal. Table sizes
1, 3, 17, 70 and 71 check that COUNT is not fixed at the currently installed 70.
Each size runs normally and with AddressSanitizer/UndefinedBehaviorSanitizer.

The clients require identical TABLE values, addresses of the TABLE and COUNT
objects, and descriptor addresses across translation units. Every descriptor's
port-object identity, pin, flags, order and device marker must match generated
literal data. Compile-time type checks and three negative compilations require
an immutable pointer, count and descriptor. One client includes only the public
header, exercising its forward declaration. A non-Zephyr compilation verifies
that it introduces no native declarations there.

Counted GPIO/readiness/clock/delay substitutes must receive zero calls. For each
normal native object, the only undefined symbol may be fixture_devices, and
there must be no dynamic initialization function or constructor section. The
sanitized objects are excluded from this section check because sanitizer
instrumentation legitimately supplies its own initialization.

Invalid-index rejection in this new test belongs to a small test consumer. It
does not prove any production owner's bounds checks. The unchanged existing
motor, opponent, QTR and power suites remain the production-owner evidence.
The synthetic descriptor checks do not establish the target representation,
padding bytes, installed device-tree pin mapping, target ELF deduplication,
startup imports, modeled loader fit, loaded free RAM or physical qualification.
Those target/source-review checks are separately owned by the coordinator and
reviewer. No board access, upload, reset, sensor activation or motor run occurs.

Initial run1 failed before native execution because the generated fixture lacked
Arduino.h. The original test freeze, test body and all failed command receipts
are retained; this is a fixture failure, not an observed production failure.
