# Independent UART fixture correction

The first Windows run had 15 passing methods and one fixture error. The changed
FD-name scenario added descriptor 9 to an enumerated list without providing the
metadata that the fake fd() lookup requires. On the second sweep this raised a
Python KeyError, rather than presenting a coherent changed descriptor table.

The independent author verified the failure against the saved traceback without
reading production. Correct only the synthetic table: when descriptor 9 first
appears, provide non-character metadata (None), and avoid duplicating an existing
name. The original requirement that changed FD sets produce INCOMPLETE remains.
Do not broaden production exception handling to hide this fixture inconsistency.

The generic output-size assertion now checks the public bounded_report emitted
body while returning raw observations for detailed assertions. The explicit
oversized-output test still requires preservation of aggregate counters.

Exact original oracle 13687B/SHA2569954e160a9bac3642087150becda84f3eacb0306bc2900cf10c7e62ddc384352
is preserved as oracle_original.py beside the unchanged first stderr/result.
Corrected oracle 13888B/SHA2561ea6116205f1ddabfbcb32f1c46a03236f10dcfb78918309c30310a389336566.
No production edits or test execution were performed by the independent author.
