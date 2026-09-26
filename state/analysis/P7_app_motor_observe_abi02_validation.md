# D194 ABI query correction, host validation and actual observation

26 September 2026. Actual attempt02 succeeded at clean reviewed
efadbe5c9e920114919e016b5af6952cda9efb6c: check-only0/execute0, one transport,
four file-tool children0/reaped/no timeout/empty stderr, all13 remote closing
checks and local closure PASS. The02 owner is consumed. No firmware upload,
reset, compiler or MCU-memory operation occurred. D190 remains latest flashed.

Actual Runner address0x20013960,169736 bytes/alignment8, end0x2003d068. All20
SIZE/ALIGN/LAYOUT groups and11windows are observed. Report1168bytes and its
polls member is unsigned int,4bytes/alignment4, offset168572 in Runner (12 in
Report), address0x2003cbdc. Alignment4 came from GDB, not a supplied constant.
The exact original readelf0x29708 size remains in raw evidence; only private
summary normalization converts it to169736. File layout does not measure live
RAM/stack or WCET and does not resolve the original runtime fault.

Actual result893020bytes SHAa5e67635f43b96b813885687fbafe743cfc3ec6a93d089a66453ca574c0676da;
abi3704bytes SHAdfc34596b65d3a82e21e28c3acf9fb1535bec2eb3b489d270c593c9fe3eab3a7;
local closure275bytes SHA3f17b83efc79026b46d519646798f70d9cf898b0c4a0bef2e06e6da4da0e84a7.
See compile_raw/native_abi_static02 and native_abi_static02_invocation.json.
The source/host preparation below preceded this separately admitted observation.

## Preserved actual failure

At clean HEAD79dc3964, corrected Windows check-only passed: four commands,
5561 UTF16 units, source3a08ddeb. Fresh ADB identity matched uid/gid1000,
arduino home, boot55c386b9-fe6d-4388-a7f4-1d91e0bb49d8 and absent scope01.
Native attempt01 then issued one transport and four file-only children. All
returned0/reaped without timeout, but GDB16.2 printed86 bytes of syntax-error
stderr for alignof(member-expression). Strict rejection was correct. All12
artifact/tool pins plus identity, and independent local closure, passed.

Original result e83afc5f/local closure589b78d1 remain FAILED and the01 owner is
consumed. No complete ABI was accepted. Partial raw data show member sizeof4,
ptype unsigned int and offset168572; its alignment numeric tag is missing.
No firmware, compiler, reset or MCU-memory operation occurred. Failure and raw
receipts are preserved in97dd06b7; preflight_actual02.json preserves admission.

## Bounded correction

Supplementary contract772615cd and sourcea0a5aef1 add inspect_static_abi02.py.
It preserves all historical source, contracts and tests. Five bootstrap helpers
are copied exactly so the original wrapper can be verified before execution.
The original projection runs first; the additional checked projection changes
only SELF, local/remote owner02, scope label, and polls ALIGN to unsigned int.
Final projected16937 bytes hashb03561df. No numeric alignment is supplied.
Current member ptype must again be exactly unsigned int before the unchanged
normalized summary. Raw result/layout, strict stderr, complete numeric tags,
BSS/windows, deadlines, source/artifact/boot checks and closure remain intact.

Independent oracle9e50373e was authored from contract and historical public
fixtures without reading the new implementation. Its freeze3d51c5c1 precedes
execution. First serial Windows and Linux runs each pass21/21 methods, no skips
or failures. All142 coordinator-frozen pins are unchanged afterward. The new
tests cover exact bootstrap bodies, original-first projection, ALIGN-only change,
private composition, provenance, observed alignment values, current-type refusal,
raw preservation, command bounds, new ownership and failure closure.

Raw host evidence: P7_app_motor_observe_abi_raw/abi02_first_windows01.json,
abi02_first_linux01.json and abi02_coordinator_freeze01.json. Existing58-method
Windows-mode/ABI coverage remains unchanged and was verified earlier in this
turn. Test output is synthetic host evidence, not accepted target ABI.

After final independent review and clean committed HEAD, check-only then one
execute may claim native_abi_static02. Never rerun01. Actual entry instructions
and separately scoped inhibited capture still follow successful ABI evidence;
original IO fault, RAM/WCET, physical acceptance and human gates remain open.


Final independent same-model source/host review9b5c29c8 PASS/no material findings.
All142pins audited, first21+21PASS receipts verified; zero owned temporary
remnants on Windows and Linux. Separate native admission remains pending.


Actual independent review e9c8d255 PASS/no material findings; all140 actuallocal
pins and142coordinatorpins match. Exactcommands,20groups/11windows/rawsymbol
normalization/BSScontainment/13remote+localclosure audited. This closes fileABI
collection only; newentryinstructions andlaternativecapture remain separate.
