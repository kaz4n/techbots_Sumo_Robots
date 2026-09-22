# Independent Robot QTR warning scenarios — 2026-09-23

Ownership: new `tests/test_robot_qtr_warning.cpp` and this report. Existing Robot
candidate files, established tests, headers and ledgers were not changed.
Read public headers and D-060 only; no implementation read, build, hardware
operation or commit. Four CHECK-only cases extend real Robot coverage.

The coordinator confirmed the public timing anchor before freeze: first admitted
fresh observation satisfying both current confirmed white and valid preceding
actual opposing nonzero duties starts qualification. Do not backdate to
`applied_us`, which does not establish that white remained continuous earlier.

The fixture enters the left-side escape row and reports its actual pivot request
on a later fresh observation. It then reports that preceding pivot setting over
a sparse interval. At the new decision, Robot must independently evaluate the
warning and advance the already-expired700ms pivot into its forward segment.
This is a legal synthetic receipt stream, not a claim of measured body rotation,
continuous physical white acquisition or a passing real-time schedule.

Covered:

- 1499999/1500000/1500001us with strict warning only at the last boundary;
  the paired base explicitly crosses uint32 micros wrap at that observation.
- Aggregated new warning mask5, source observation timestamp and escape timeout
  event; warning retains EDGE_ESCAPE, valid bounded motor permission/request,
  line mask and no core/escape fault. It does not suppress edge handling.
- A subsequent nonpivot actual receipt clears the warning. A real replacement
  enters another pivot and a second complete qualification emits a fresh warning.
- Disabled actual output or either actual wheel zero breaks qualification despite
  a prior opposing request. Current black also breaks it despite a held pivot
  receipt, while escape still finishes its forward segment.

Static pass only; no execution by this author. No REQUIRE, unsafe private-state
mutation or fabricated historical timestamp is used. Coordinator must run the
host and sanitizer suites and record their separate receipts.

Coordinator build follow-up: the first host compile failed because this new
unlocked file lacked the direct `<initializer_list>` include needed for braced
range loops. The raw compiler receipt is `P1_robot_host_20260923.txt` (exit2).
The coordinator added that one include; all four cases and their predicates are
unchanged, and no locked file was altered. This is a literal portability fix,
not an assertion change or a passing execution receipt. A subsequent coordinator
run is separate evidence; this author did not run it.

Original frozen SHA-256:
`F5DB4733122ABAF2996D5A8D60CB01C2116476B9BDDD047CB869F98D62D6F2C8`.
Revised include-only SHA-256:
`2C74E501769FD87ED17499D775411C4F3AE2D257A52F27161CE3164B9388890E`.
The other65 Robot cases and their hashes remain unchanged.
