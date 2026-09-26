# D199 SETTLE entry reader source and host review

26 September 2026, Asia/Dubai. Separate fresh-context, same-model reviewer;
review only, with no implementation or test edits. This review covers the fixed
file-entry wrapper and the first frozen Linux/Windows host results. It does not
review a native entry attempt or actual instruction semantics.

## Findings

No open BLOCKER, MAJOR or MINOR finding in this scope.

## Exact reviewed inputs

Paths below are repository-relative. Raw inputs, historical failures and original
test files remain preserved. The reviewer independently rehashed all 204 entries
in the coordinator freeze after both host runs; all lengths and hashes match.

| Input | Bytes | SHA256 |
|---|---:|---|
| state/analysis/P7_motor_settle_entry_contract.md | 19485 | af8ce726bf49b79fecc07548bd78a808d788894ea9e9e1b59daa69eae8a54e7d |
| state/analysis/P7_motor_settle_compile_raw/entry_binding01.json | 20870 | 6234676242fdd7e61136fd2a1f66fabb0242b10ee597ef2bf6555a9444ecfd2b |
| state/analysis/P7_motor_settle_compile_raw/inspect_static_entry.py | 10425 | c9e8f023ffc853dce951b05c24cbd55bef04270682c3d271cb1087b2fa67ab81 |
| tests/tooling/test_motor_settle_entry.py | 13633 | 4e6e1caed73b3612d63319e6b15e827cce941e0e365f755083774ed9396f49f6 |
| state/analysis/P7_motor_settle_compile_raw/independent_test_entry_freeze01.json | 39074 | 47a8af8f88ddbf2342a148c4a7a442c1acbfcedf12c9ed4a8c133845fc33d08e |
| state/analysis/P7_motor_settle_compile_raw/entry_coordinator_freeze01.json | 40813 | f16dceb9777bc9097fb73f947c8002273dad5cfe1e9072dca79139096e2dcae6 |
| state/analysis/P7_motor_settle_compile_raw/entry_host_driver01.py | 2692 | 05648c2067f7ceafe2a8501917e3e8762bcdc66ce2fc3339c83f482d8ea5d8bc |
| state/analysis/P7_motor_settle_compile_raw/entry_host_closing01.json | 640 | 1d798f2491b136c85201b2e3848b10808a5b7aa725eb6d45f27c485cab15923a |

The independent freeze records 200 input pins and explicitly declares freezing
before its author's first read, hash, import or execution of the new source.
Its subject identity is labelled author-reported. The coordinator subsequently
froze 204 inputs including implementation, oracle and freeze evidence. The
reviewer inspected this recorded independence boundary, not an externally
attested account of the author's private state.

## Source and fixed-evidence checks

Read AGENTS.md in full, current handoff/resume/progress, D199 and the active P7
scope. Current date is 26 September; software work and this review confer no
scheduled or physical gate. D195 remains the latest flashed image.

Independent AST and byte inspection confirms the five bootstrap helper bodies
are byte-exact copies of the accepted D199 ABI wrapper. This retains ancestry,
plain regular single-link files, reparse and descriptor checks, bounded reads,
before/after identity, digest and primary-error/close behavior. The Windows
executable-extension 0111 exception remains narrowly conditional, with the
existing cross-API ctime handling unchanged. There is no broader mode mask.

The exact nine reader and 36 parser replacement tuples equal the adopted
binding, including ordered counts and newline bytes. Independently applying the
literal historical projection chain as data, without importing the subject,
produces the required 17061-byte reader input 67ff238c and then:

- Reader: 17085 bytes,
  db4122376e7ef2da92ca49633b01248514274744b429ad54bede8d0c8d8da9f8.
- Parser: 10562 bytes,
  7f96678955bc37082766f3b02b46b1cdbba832624815b1ba4266a549d3e372f2.

Import is passive apart from module-location calculation. Main checks exact
list/string CLI types, fixed action/HEAD shape and -B before loading, then
delegates once. All eight ORIGINALS and the contract are checked before private
execution. The saved D199 projector runs before the supplementary entry
projector; every nested loader remains active. Fresh private ModuleType objects
retain original absolute source paths, avoid __main__/sys.modules and do not
call the historical entry load/main. HARD_PINS is copied and extended. Entry
queries and summarize are assigned directly from the same parser namespace;
the inherited ABI summary is not invoked on an entry packet.

The final projection retains the reviewed attempt implementation: exact source,
artifact, boot and tool admission; clean reviewed HEAD; fresh local owner and
absent remote scope; 128 MiB local guard; 30000 UTF16 command bound; four fixed
file children with 60-second deadlines, 5-second reap and 1 MiB streams; one
400-second transport; raw result preservation before summary parsing; exact
remote closing checks and independent local closure; first-error preservation
and consumed-owner refusal. No arbitrary source/range/profile CLI is added.

The reviewer independently parsed accepted raw readelf stdout 4aece135, checked
all 31 exact function alias rows and six initialization bound rows against the
binding, and confirmed the separate 28-byte LOCAL OBJECT at 0x2003d3e8. All 29
fixed ranges total 3038 bytes. Both constructor aliases remain mandatory. The
publisher is LOCAL and native SETTLE GLOBAL; Thumb addresses, sizes and section
identities match. The accepted ABI did not observe initializer bytes. The entry
parser still requires their future observation as 05011008 at 0x081162d8.

Queries retain the four specified file commands and guarded file GDB settings.
There are exactly 59 expressions: 29 ordered marker/disassembly pairs and END,
with literal backslash-n echo suffixes. Exact unique symbol tuples, section
containment, initializer pointer/bounds, ordered markers, headers/end markers,
recognized opcode widths, unparsed-address refusal and contiguous full range
coverage retain the historical parser semantics. Report field ABI parsing stays
in the separately accepted ABI evidence; no invented entry summary field is
introduced.

## Independent fixtures and actual host receipts

The oracle uses the contract/binding and pinned historical public fixtures.
Static comparison confirms all 19 historical methods and all 77 historical
assertion call sites remain after 12 explicit fixture/metadata substitutions;
77 is a source call-site count, not a runtime assertion total. Changes update
scope/addresses/counts and the local publisher classification. The former extra
marker becomes 29 so it remains an invalid extra marker with 29 valid groups.
Both constructor-alias and initialization-bound mutation targets remain intact.

Four added methods cover actual accepted symbol/binding evidence; both added
functions' missing/duplicate/wrong binding, Thumb, size, type and section
refusals; markers and incomplete/malformed/overlapping disassembly for each new
range; and a sentinel proving direct entry summary replacement never calls the
ABI summary or requires ABI tags. Synthetic instruction packets test parsing,
not actual emitted instructions. Historical cases retain passive import, CLI,
input checks before execution, private composition, fresh ownership, real
prepare, mocked execute/raw persistence and primary-failure/closure behavior.

The reviewer did not rerun tests or invoke any device command. Saved receipts
were checked against saved stdout/stderr hashes and the exact 23 selected test
names. Both first runs returned zero, every method is reported ok, no skips or
timeouts appear, stdout is empty and changed_inputs is empty:

| Platform | Passed | Result bytes | Result SHA256 |
|---|---:|---:|---|
| Linux | 23 | 645 | 6caf4bde15d5f7a58cf749469df9a045a68f41f1189eff799068d148a33b4171 |
| Windows | 23 | 567 | 1d229c818d36f7ff9006b0aeab9aa4e28a9bacbf5a0110a9b0c12ba0b449c429 |

Linux began 10:55:19.570525+04:00 and completed in 11.856342 seconds; Windows
began 10:56:26.244464+04:00 and completed in 1.463755 seconds. These were serial
runs. Stderr hashes are 654b5d3d for Linux and bec9a011 for Windows. Coordinator
closure records all 204 pins unchanged and no new bytecode. The reviewer's final
independent 204-file hash/length check agrees. No repair or retry was needed for
this entry oracle. Existing ABI and other historical failures remain preserved.

## Verdict

PASS for the exact D199 entry wrapper, adopted binding and controlled host
validation above. No firmware, config, pin, safety limit or locked test change
is part of this review. Local native_entry_static01 was absent when inspected;
no fresh remote absence or same-boot admission is asserted here.

Next: admit and review a fresh fixed file-only scope at clean reviewed HEAD,
then collect once and separately review its actual initializer/publication and
SETTLE instructions against the accepted ABI and source. Parser success alone
does not establish store ordering, first-failure retention, hardware-call order
or bounded target paths. No upload, MCU read, target execution, electrical
inhibition, root-cause diagnosis, live RAM/WCET qualification, motor permission
or human phase gate follows from this source/host PASS.
