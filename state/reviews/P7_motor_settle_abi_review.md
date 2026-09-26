# D199 SETTLE report ABI wrapper: source and host review

Verdict: PASS for the corrected wrapper and final controlled host evidence. Both material review findings were resolved with preserved prior evidence: one production query-escaping defect before execution and one fixture identity/coverage defect after the first passing host runs. No material source or host-coverage issue remains in this scope. Actual target ABI observation is still pending.

Reviewer: separate same-model agent, reused context, 2026-09-26; local read-only source, AST, byte reconstruction and saved-receipt review. No subject import, test execution, compiler or device calls by this reviewer; only this review was written. The independent oracle author froze the initial oracle before reading, hashing or importing the new implementation. This reviewer did not share implementation clues with that author before freeze.

## Frozen implementation and contract

Contract `state/analysis/P7_motor_settle_abi_contract.md`: 22405 bytes / SHA256 `dfc762768731cf53ef1240a0d9eabface824ad96a72f3dfeaa1824c72332d956`. Wrapper `state/analysis/P7_motor_settle_compile_raw/inspect_static_abi.py`: 16106 bytes / `0f2b37c906a8ad78d596a1256af94d67d3d47793f6025a5e9dc4449d928002ea`.

The earlier contract `a0e96100...` is preserved before its bounded amendment. Six GDB queries for unused inline constexpr validity constants were removed before implementation/oracle execution; masks 1/2/4 and allowed mask7 are explicitly pinned-source semantics, not target observations. The actual valid-field offset/width remains required. D198's saved -g/-Os recipe does not guarantee unused-symbol debug visibility; their absence in this artifact was not observed or asserted. This distinction is consistent with [GCC's debugging documentation](https://gcc.gnu.org/onlinedocs/gcc/Debugging-Options.html). No fallback after a failed target query or compiler/source flag change was introduced.

Independent data-only reconstruction confirms all fourteen ordered, count-checked substitutions through the historical D194 and ABI02 chains: exactly 17061 projected bytes / `67ff238ce7a9f847e53d98fb4f3c47f02bbea12c51a1062457f1583a9399acc6`. All five copied bootstrap functions are source-exact ABI02 bodies, preserving the narrow Windows executable pathname execute-bit adjustment, existing cross-API ctime exception, complete same-API stamp stability, ordinary/single-link/reparse checks, bounded descriptor reads and first-error/close behavior.

The loader verifies all five complete original inputs plus the contract before private ABI02 execution. It retains original-first composition and historical pins, adds the new D198 launcher/manifest/result/artifacts and contract, injects only the fixed expression provider, and wraps the saved summary. It does not copy or replace transport, prepare, claim, execute or closure methods; does not instantiate an owner during loading; and does not register modules globally. Import remains passive, and main checks exact arguments and Python -B before loading.

The D198 source/artifact binding remains the separately reviewed successful compile `117cc0e7...`, manifest `aa314548...`, result `9b7f0c44...` and artifact packet `e18384c1...`; no D193 artifact or stale address is substituted. The fresh local ABI owner is `P7_motor_settle_compile_raw/native_abi_static01` and remote absent-scope guard is `app-motor-settle-abi-static01`. Four file commands, existing no-autoload/no-inferior-call GDB options, child/stream/transport/command limits, 128 MiB local-space guard, 13 remote final checks and independent local closure remain inherited.

## Query, parser and object evidence boundaries

The fixed query has 23 SIZE/ALIGN/LAYOUT subjects including terminal bool, all eleven existing Runner windows and 223 expressions. Sample, Report and Reason occur immediately before report_.polls, preserving its contiguous unsigned-int type guard followed by bool. The 62 appended expressions measure eleven offsets/widths and nine enum values; no unused validity-symbol queries remain.

The new numeric parser requires the complete new-marker sequence in exact order, unique integer answers and exact required values. It validates Sample12/alignment4, Report28/alignment4 and Reason1/alignment1. Summary delegates exactly once on independent deep copies, retaining original normalization/polls evidence and caller-owned raw result/layout. The report stays a separate global object, not a Runner-relative window.

Symbol candidate selection uses the complete expected mangled name before filtering kind/binding, so duplicate conflicting rows fail. It accepts decimal and lowercase0x sizes, requires one OBJECT/LOCAL/DEFAULT row and numeric section, and derives address/name from that row. The report must match observed size28 and alignment4, share Runner's checked NOBITS .bss index, match observed/check-packet section address and size, lie wholly inside the initialized BSS subrange and remain disjoint from Runner. Merely lying in the larger .bss is insufficient. Accessor retention is not required. No current report address or entry range is assumed.

The initial source `6faa240e...` used actual LF characters in three echo suffix literals, violating the contract's literal backslash-n strings. AST inspection distinguished runtime byte[10] from inherited bytes[92,110]. Commit `f4c8c6aa` preserves that pre-execution finding/source. The final diff adds exactly one backslash at each of the three sites, affecting all 31 emitted echo strings; AST inspection confirms [92,110] at each corrected site. No test or native run of the defective source is claimed, and no other production change accompanies the fix.

## Independent fixture selection and correction

Initial oracle `tests/tooling/test_motor_settle_abi.py` was 30770 bytes / `04f4ed1405eaa34a6d66dce754d62dcd1babe808dcfbe90087daebdc10eaf4cf`; independent freeze01 was `9b54d11469c656582ae9b6f83d8c167ad3e7fe65b766c92f80150ed890895d98`. Its explicit selection is 11 bootstrap +7 ABI parser/receipt +14 lifecycle +14 Windows-mode methods, plus20 new methods. Old fixed target-count/projection assertions and entry tests are explicitly excluded, with replacement current-target assertions or deferred entry evidence identified. It does not claim to rerun every historical method as D199.

The selected historical assertion bodies are checked through the original oracle hash and three scope-literal replacements, with explicit metadata globals and an extended synthetic packet. Actual projected D198 compiler admission, artifact validation and prepare are exercised with current inputs; subprocess/network endpoints remain controlled. New tests cover exact queries/projection/private composition, all-input-before-execution checks, real current header admission, previous D193 artifact refusal, deep-copy mutation protection, all numeric mismatches, observed type sizes, malformed/duplicate symbols, zero-BSS edges, Runner overlap and raw-first failure/closure behavior. Windows mode tests exercise the new wrapper with unchanged historical assertions.

First Linux66 PASS and Windows64 PASS/2 skips are retained with oracle/freeze at `e3e69d9e`; no host failure occurred. Review found a narrower coverage defect: appending the synthetic report after Runner changed an inherited last-row duplicate case into a report-duplicate case. This could pass while omitting the intended duplicate-Runner subcase.

The corrected fixture inserts the report before the original final Runner row and selects the new report test's row by its complete PROBE_SYMBOL suffix with an explicit uniqueness assertion. The exact two-site diff retains all prior assertions and66 methods; it changes no production source or lifecycle mock. Thus the unchanged inherited duplicate case again targets Runner, while new report mutations still target the report. This is restored fixture identity/coverage, not a repair to make failing code pass.

Final oracle: 30983 bytes / `96763b42d61b80654503f4093d32ac3b174ab2152fdfb795b3801304e4e2b252`. Independent freeze02: `46c51e3f3fffaaa83a37cc9cfe91a045b0b6c219d925a730918ea327330bd661`. Coordinator freeze02: `89cb2daf4b9e3098e07fff66a21ff5ba8ae32cf5810c2ddb10803b2690687cf7`.

## Actual final host evidence

All paths below are under `state/analysis/P7_motor_settle_compile_raw/`. This reviewer read both rounds, verified saved stream hashes and independently rehashed all192 final coordinator pins with zero changes.

| Final receipt | Outcome | Result SHA256 |
|---|---|---|
| `abi_corrected_linux01/result.json` | Exit0;66 PASS,0 skips;13.776 s unittest /19.678 s outer | `98fd35bd42a9a27f1514fb786675cbda3667adf1fb238d20cb9fe49c4b795d54` |
| `abi_corrected_windows01/result.json` | Exit0;64 PASS,2 skips;3.179 s unittest /3.343 s outer | `218d732cc730b885e8351e0b05e1f56779560b7a48c3cbfdeb7fbf0ba898ad63` |

Windows skips are exactly `test_real_file_and_parent_symlink_refuse` (WinError1314, unavailable symlink-creation privilege) and `test_regular_to_fifo_swap_is_nonblocking_and_never_read` (Linux FIFO fixture). Both execute successfully on Linux. All other mode cases, including the real executable-named file read without launching it, pass. Both invocations report no changed inputs; stdout is empty and saved stderr hashes match the receipts.

Closing receipt `abi_host_closing01.json`, 716 bytes / `67b640ce196a848318902b3a429210d97e33fced8b5a7ad5a70f4068c3fb061a`, binds these results and reports192 stable pins and no owned Linux/Windows temporary fixtures. The new local native ABI owner is still absent at reviewer inspection.

These are synthetic host parsing/lifecycle results. The separate report's actual target symbol, address, layouts and enum answers remain unobserved. A clean committed execution HEAD and unchanged native scope/admission must precede the one file-only attempt. Actual emitted stores/initialization and entry semantics require subsequent instruction review using newly observed ranges. MCU contents, coherent capture, failure cause, a firmware repair, WCET, physical qualification, motor permission and human gates remain outside this PASS.
