# D171 active diagnostic compile route

IMPLEMENTED / HOST-TESTED. Source1a89c4a1, caller84efd006; no native operation
in this validation. The existing caller gains only active01 ownership/flags and
per-instance local staging paths. D170 explicit staging preserves retained data.

Independent final test7c27f792:16/16 PASS,0.145s,first execution. Existing unchanged
test_compile02:12/12 PASS,0.149s. Commands ran Python-B under WSL Ubuntu with
isolated empty pycache prefixes and owned RAM fixtures; transport/compiler calls
were controlled substitutes. All12 frozen inputs remain exact. The unexecuted
draft449c4698 is preserved; pre-execution review corrected raw-byte read spying,
error mapping and cache preconditions without changing production or requirements.

Actual Windows local admission also passed all117 pins with transport/Popen
guarded against execution: active owner/output absent, legacy stage retained,
selected inert flags exact. Inputb91cf39c changes exactly five hashes from the
historical02 set; source filenames remain103src+3bench. Both old manifests and
ENV/IDENTITY/REMOTE_CHILD/extracted_wait bytes are unchanged.

Evidence: P7_motor_fault_raw/active_legacy.json, active_local_admission.json,
active_freeze.json and active_first.json. Separate fresh-context same-model
review: state/reviews/P7_active_compile_review.md,
SHA256c9781e61d9d92de78b49c57ee76a0822c02d46fd64ec7f9a5072f90b5c7eac67,
PASS/no open findings; includes prepared plan41d697b2 and new manifestb91cf39c.
Reviewer inspected root-run results and did not perform native operations.

Next operation is separately identified by D172 and
P7_motor_fault_active_compile_plan.md. Host green does not establish a compiled
artifact, upload, diagnostic execution, original fault cause or any physical gate.
