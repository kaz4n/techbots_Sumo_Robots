# D167 fresh compile ownership, existing implementation

The D165 compile01 attempt is consumed. D166 changes only diagnostic enum names.
Reuse the existing bounded caller for a distinct attempt without cloning it,
overwriting its old input manifest, or rebinding module globals.

Public interface: CompileOnce(*, run_id='compile01'). Accept only the exact strings
compile01 and compile02; reject other values before file or transport activity.
Each instance exposes run_id, output, inputs_path, remote and sketch. For compile01
retain native_compile01, compile_inputs.json, motor-fault-compile01 and its
motor_fault child. For compile02 use native_compile02, compile_inputs02.json,
motor-fault-compile02 and its motor_fault child, beneath the same fixed parents.
Keep shared local staging at build/stage/motor_fault; it must be absent on entry.

All operations use the instance's selected paths: manifest checks, output/command
receipts, isolated pycache prefix, remote preamble/claim/source checks, ADB push
destinations, checked compilation and final policy checks. No selection leaks
between sequential/nested instances, and no module global is assigned by a run.
Default constants may remain for historical/public fixture compatibility.

Add pure parse_request(argv): ['--execute'] selects compile01;
['--execute','--run','compile02'] selects compile02. Every other spelling/order,
extra argument or type fails before constructing an instance. The entry point
uses that parser; run() verifies its invocation matches its selected instance.

Preserve IDENTITY, REMOTE_CHILD, ENV and extracted_wait code exactly. All source,
tool, process, deadline, output, recipe, artifact and final checks remain. No new
upload/reset/build flags or source overlay. Old compile_inputs.json and all old
receipts/tests remain unchanged; it must reject the edited caller/current source.

Author independent companion checks from these interfaces: closed selectors,
default paths, explicit02 paths, interleaved instance isolation, selected manifest/
cache/preamble/receipt/compile routing, unchanged child machinery and preservation
of the original manifest. Controlled substitutes only, no native action. Freeze
before execution. A new117-input manifest, concrete plan/review and scoped one-shot
decision precede the actual corrected-source compile; this contract is host-only.
