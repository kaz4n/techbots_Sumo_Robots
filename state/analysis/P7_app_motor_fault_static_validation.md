# D187 fixed static diagnostic adapter validation

25 September 2026, Asia/Dubai. IMPLEMENTED / HOST-TESTED; scoped final review
recorded separately. All packets and compiler responses in tests are synthetic.
No compiler, board connection, target artifact, upload or firmware operation.

Source9759091b plus portability repair39eac0a1 implements only
tools/app_motor_fault_static_policy.py, current SHA256
3e5d49e4a70c0cf6197e26b1ba5ce2b7e07601bf5d9250ba430f90d1f9eab270.
It privately reuses unchanged D141/D147 validators with exact expected-name/flag
substitutions and a seven-file artifact alias map. Raw compiler input, caller
paths, artifact bytes and complete inherited report remain unchanged. Flat
export/build equality and all inherited layout/init/package/TLS checks persist.
Generic/dynamic admission, shipping firmware/config and locked tests are unchanged.

## Independent tests and preserved failures

Separate fresh-context author static_trace_policy_tests used the contract and
permitted public synthetic fixture/report mechanics, never adapter or validator
implementation bodies. Original33-method oracle a1438176 was frozen1a7a1a1a
before execution, with12source/contract/fixture identities. Corrected oracle
e6d52ec6 and source3e5d49e4 were refrozen39eac0a1 before the second run.

| Receipt under P7_app_motor_fault_static_raw/ | Actual observation |
|---|---|
| freeze.json | Original12pins,33methods and author provenance |
| first.json | WSL33methods:14reparse-injection subtest failures and1helper-path error |
| windows_first.json | Windows28methods:24errors exposing real path/handle timestamp incompatibility |
| windows_stat_observation.json | Four unchanged files: path/path and handle/handle stamps stable; only cross-API ctime differs |
| correction_freeze.json | Bounded source repair and new-fixture corrections;10other pins unchanged |
| corrected_linux.json |33/33PASS,51.622s, no skips |
| corrected_windows.json |28/28PASS,8.333s, no skips |
| integrity.json |12current/Git pins exact, protected inputs unchanged,0owned RAM fixture remnants |

The Windows repair retains full before/after comparisons within each stat API,
all identity/size/mtime/attribute comparisons across APIs, and the complete Linux
comparison. It excludes only Windows cross-API ctime equality, which rejected
unchanged ordinary files. Every plain-path/reparse/hash/size guard stays active.

The independent new fixtures had two defects: old helper default BUILD differed
from the supplied validation path; and mocking os.lstat did not intercept
Path.lstat's os.stat(follow_symlinks=False) route. Explicit fixture path arguments
and both non-following stat routes correct these; every rejection assertion
remains and each reparse case additionally proves the injection was observed.
The coherent old-profile negative also now uses the intended path. Original
source, tests and failures remain committed806a3603 and earlier freezes.

Coverage includes all84controlled command properties, exact profile/JSON/path
checks, no mutation of historical consumers, all seven actual filenames, original
byte-object forwarding, exact inherited report, export equality, six TLS symbols
across all three ELFs and malformed ELF/package rejection. WSL alone runs the five
dependency/isolation methods with owned RAM copies and real symlinks; Windows
runs the28public metadata/artifact methods. Reparse attributes are also simulated
with proven injection. This does not claim a real Windows junction test for D187.

## Remaining dependency

The adapter has no command dispatcher and does not establish that the new sketch
compiles or fits. Next compose its one fixed static/default/M0 compile-only caller
using existing bounded transport/child execution, fresh source/stage/attempt pins,
one expanded-properties query and one compiler dispatch. Preserve checked CLI
initialization, installed dependencies, exported/build equality, failure receipts
and independent closure. Do not broaden generic/dynamic admission or mutate old
scopes. Test that composition with controlled commands before a separately
reviewed native invocation. Fresh ET_EXEC/native initialization/ABI/capture
identities, the original full-app I/O diagnosis, RAM/stack/WCET and physical/human
gates remain pending. No D149 address or D173 isolated-decoder reuse is justified.
