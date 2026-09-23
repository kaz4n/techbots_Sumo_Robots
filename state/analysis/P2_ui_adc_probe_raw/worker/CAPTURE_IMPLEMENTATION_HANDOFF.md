# D114 capture implementation handoff

Objective: decode the enabled UI Runner truthfully and collect it using only
the adopted finite MEM-AP sequence. Modified production file is only
`tools/ui_adc_capture.py`, SHA256
`f4b3db265bdf2d5a5fdada19ed9f51a44304d9ba5da8be78e598365afa2c4444`.

The pure decoder retains actual public values and both complete Runner hashes;
padding/private bytes participate in equality but are not interpreted. FAULT,
nonterminal, malformed and unstable evidence remain distinct. The collector
checks the pinned input files and ELF layout, then admits only the exact ordered
flash/list/node/Runner reads and repeats the identity brackets. Worst-case plan
is22 reads,588016 bytes,26 commands under the unchanged D104 ceilings.

`first_capture_source_freeze.json` records the complete source before static
checks. AST parsing/compile-only and whitespace checks pass;46 functions have
maximum35 lines. `first_capture_static_checks.json` records those checks.
No implementation module, generated capture command or independent test was
executed by this worker. No test body was read. No board action occurred.

Initial contract02b101fc and first source remain preserved. The later5462551a
full-BSS clarification requires no code change: `_accept_node` checks all9893
BSS bytes against SRAM before checking the9892-byte Runner. Supplemental
`capture_bss_contract_binding.json` binds that clarification without rewriting
the original receipt. P0 helper and MEM-AP configuration hashes are unchanged.

Next: independent frozen decoder/collector fixtures execute this source, then
separate source/command review. Implementation remains unchanged pending concrete
findings. Exact input-directory preparation is coordinator-owned. This handoff
does not authorize upload or readout, prove physical timing, accept A1 wiring,
qualify a button circuit, establish ADC shutdown or advance a human phase gate.
