# D155 fixed startup launcher validation

IMPLEMENTED / HOST-TESTED / scoped review PASS, 25 September 2026 Dubai.
No native scope, upload, reset or MCU collection has run.

Current source6f86e645 implements [contract](P7_static_startup_launcher_contract.md)
2bdbc3c9. It composes the completed D153 collector and D154 uploader with the
existing D144 artifact packet, frozen source checks and F166 file-only inventories.
Separate durable intents gate one upload and conditional capture; uncertainty
stops further upload/capture. Collection and observed startup remain distinct.

| Check | Actual result | Evidence |
|---|---|---|
| Independent public tests | 30/30 PASS,0.046s,exit0, first execution | [Freeze](P7_static_startup_raw/launcher_freeze.json), [receipt](P7_static_startup_raw/launcher_first.json) |
| Code-informed reviewer adapter tests | 10/10 PASS,0.119s,exit0, first execution | [Freeze](P7_static_startup_raw/launcher_private_freeze.json), [receipt](P7_static_startup_raw/launcher_private_first.json) |
| Actual local frozen-input composition | PASS; zero dispatches | [Composition](P7_static_startup_raw/launcher_composition.json) |
| Separate same-model reused-context review | PASS; no open material finding | [Review](../reviews/P7_static_startup_launcher_review.md)26fcf2f7 |

All frozen test inputs remained unchanged. Tests substitute callbacks/processes;
they are not a board upload. The actual local composition validates16 additional
pins plus17 runner inputs and the existing102-file staged source. The checked
working manifest contains103 files; the composition receipt's source_file_count
is null because that attempted projection used the stage receipt, which lacks
that field. The original raw receipt is retained without rewriting it.

The six exact command forms include26 installed dependency hashes, original
packet inspection, two frozen prerequisite inventories, upload and capture.
Final upload/capture commands measure28,068/24,981 UTF16 units, below30,000.
Only RAM payloads were created; no copied firmware, source tree or installed tool.

Before first execution, review repaired wrong recorded remote evidence paths,
output-identity checks occurring after numbered receipt creation, and a native
FAILED result otherwise returning a zero process exit. Initial inspected draft
4d5ef660 preceded the first saved draft7149bfb6 in0cdfa50b; the latter also added
independent local checks before commit. Further sources are preserved infdbd3cb5
and3bcc8219. No public test or frozen helper changed for these repairs.

Next: identify and commit the exact one-shot inert scope, binding this launcher,
tests and reviews to the current reviewed HEAD. Recheck the bare board, original
packet and prerequisites through this launcher, then permit one M0 upload and
conditional passive capture. No motor-capable firmware is authorized. Native
startup, live RAM/WCET and human/physical phase gates remain unproved here.
