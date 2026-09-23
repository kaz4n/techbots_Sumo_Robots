# D104 retained failures and correction evidence

The first policy test command used no tests/tooling PYTHONPATH, so legacy modules
could not import test_tools. Additional new coordinator fixture errors used an
incorrect installed data directory and expected SystemExit from the direct API,
which correctly raises ValueError. Corrected fixture/environment only; all75
legacy methods remained unchanged. Original d104_policy_initial/corrected logs
are retained in P2_app_build_raw; new8 cases then passed. Subsequent final suite
adds two upload guard cases after independent source/ELF approval.

Reviewer D104-R1 found a real production-probe deadline gap: timely completed C
could set FROZEN before the final clock observation reached the201s deadline.
One bounded change checks that actual endpoint, preserving the genuine completed
C, Runtime RUNNING and first failure. Unchanged independent regression changed
from fail to pass in normal and ASan/UBSan; see review raw host receipts. Initial
target/source1cd2f6cc is retained, superseded by exact2bd817c4. No MCU loaded the
old probe. Target audit-only Windows path normalization error is also retained.

The independent decoder suite passed on its first run,24methods; no oracle
changes. It was written from frozen contract/public ABI without reading Python
implementation, but its author had earlier implemented the C++ probe; this is
not full fresh-context independence. Separate reviewer inspects capture guards.
