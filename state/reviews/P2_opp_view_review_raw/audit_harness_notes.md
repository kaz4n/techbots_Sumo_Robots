# D107 reviewer harness notes

The first combined --zero --author invocation left the copied config's temporary
TICK_US=0 active for the author's normal and polarity profiles. Those profiles
correctly refused enabled setup with CONFIG and therefore failed their ordinary
expectations. Original command/output and nested receipts are retained. The
reviewer harness now restores the original config bytes and checks their hash
before further suites; no production source or author assertion changed.

The generic-target startup witness extractor initially requested the C2 alias
of ZephyrSerialBuffer's constructor. Objdump prints its shared address under
the C1 alias. Selecting that actual label fixes extraction; both symbols refer
to the same function. ELF/source identity and the extra-initializer finding
were unaffected.

Interim23a24bb0 source was observed and hashed but changed before the reviewer
could archive it. review_passive.py reconstructs it by reversing only the two
passive-admission statements in corrected1be9bc51, then requires the complete
known23a24bb0 SHA256 before compilation. The retained file is explicitly a
hash-verified reconstruction, not an originally archived source.

The first private policy copy omitted the unchanged D100 default_receipt fixture.
The new15 cases passed; two legacy classes failed setup with FileNotFoundError.
policy_1790193630381612019.json retains that execution. Copying the exact original
fixture allowed unchanged15+85 cases to pass in policy_1790193719040116930.json.

The first checked-target aggregate calculation sorted POSIX path strings and
failed its aggregate assertion while all96 per-file hashes passed. The existing
board.source_hash sorts native Path objects; this Windows-produced source adds
uppercase README.md, revealing the difference. review_checked.py now explicitly
uses PureWindowsPath ordering to reproduce that producer on either platform.
No source bytes or production hash algorithm were changed by the reviewer.
