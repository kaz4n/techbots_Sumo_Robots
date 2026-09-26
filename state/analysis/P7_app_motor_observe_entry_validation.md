# D194 observer entry inspection preparation

26 September 2026. HOST-VERIFIED preparation only; no actual entry query yet.
Contract437f8cb8 and source0c3a3dd1 privately compose the unchanged ABI02 reader
and historical entry parser. No transport/attempt lifecycle is copied or changed.
The five bootstrap helpers are exact copies; all six inputs are verified before
private execution. Reader projection16955/93729533 changes only identity/owners/
labels; parser projection10333/6a82a9e5 changes only the observed symbol ranges,
Runner namespace and fixed build path. Historical source and tests stay intact.

The successful ABI02 readelf stdout158577B/b3542b0d confirms all27 function groups
and aliases, section1 text range, section2 initializer bounds and the constructor
symbol. Initializer bytes and actual instructions have not yet been collected.
The new reader directly installs entry queries/summary, avoiding inappropriate
ABI polls-tag checks on instruction output. Four bounded file-tool children,
strict stream/closure checks, source/artifact/boot pins and fresh owners remain.

Independent oracleb7db0b43 was frozen before its author read the implementation.
First Windows and Linux runs each passed19/19 methods with no failures/skips.
All150 coordinator-frozen pins remained unchanged. Tests cover exact projection/
bootstrap/private composition and pins; complete synthetic27-range packets;
decimal/hex sizes and opcode widths; aliases/symbol/type/Thumb/section errors;
initializer bytes/pointer; marker order/duplicates and truncated/discontinuous
instructions; raw retention, prepare bounds and failure closure. Synthetic
instructions test parser framing, not target instruction semantics.

Evidence: P7_app_motor_observe_abi_raw/entry_independent_freeze01.json,
entry_coordinator_freeze01.json, entry_first_windows01.json and
entry_first_linux01.json. Native owner native_entry_static01 is unused.
Final independent review and clean committed HEAD precede check-only and one
separate native observation. Its instructions require semantic review before
any newly scoped inhibited firmware upload/capture. No motor/physical gate follows.

Separate next-run preparation: upload_scratch_inventory01.json is a bounded
read-only observation of three current D190 uploader copies. It proves no
absence of process use and performed no deletion. Future upload needs separately
bound cleanup and an observation interval appropriate for the longer diagnostic.


Final independent same-model source/host reviewd52c4cb8 PASS/no materialfindings.
All150pins and19+19PASSfirstresults audited. Ready for separate cleanHEAD native
admission; file instruction collection and semantics remain unobserved.
