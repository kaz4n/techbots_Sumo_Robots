# D112 A1 raw/decoder bench validation

IMPLEMENTED / HOST-TESTED / TARGET-COMPILED / REVIEW-PASS, no open findings.
Final review JSON SHA5753c8cdfe63edefd971f6ff29111c0ca4ea2fe28d8ff7c28756d3b645ccb662.
Physical B6 and every human gate remain pending. No new MCU upload/reset/run.

Contract/config/interfaces e898cf3 and literal compile route5182f17 precede this
implementation. D051/D075 authorize software preparation. One Reader performs
beginWithButtons/readButtons only; actual ui::decodeButtons output accompanies
the first128 admitted immutable samples. Invalid, ambiguous and unconfigured
decoder diagnostics remain evidence, never a fabricated release or button-level
qualification. Actual sample and decoder provenance are separate after a bad
closing clock. No matrix, motor, Runtime or transport owner is introduced.

## Implementation and independent tests

Pre-execution review clarified that saving the returned sample and sample_seen
must precede the immediate A clock. The implementation changed only that two-line
ordering before independent test freeze/execution. First source9c0382c9 and its
target0b6a559e are retained as superseded, not accepted D112 artifacts. Corrected
sourcebc2def36, Nativea9bd1c4d, header881eceb2 and sketchbe6dd812 remained frozen
through all tests. Eight strict syntax profiles PASS;30 functions/max23lines.

Author expectations came from adopted contracts/public headers, without reading
implementation bodies. This reused separate same-model contexts, not cross-model
or fresh whole-repository gate review. Frozen cases0bf8fd65 and harness6fe51268
passed first execution unchanged:30 executable profiles/65 isolated commands.
Normal and ASan/UBSan each35cases/21,759assertions; Native startup/default10000loops
each2/27. All16384 raw codes were checked in valid-window and overlap profiles,
normal/sanitizer each278,704 and278,656assertions respectively. Zero/one capacity,
invalid wrapper/native/decoder configs, source/clock faults, immutable captures,
missed-release saturation and aggregate half-range rejection all passed. Three
unsafe flag compilations refused. Five live registry profiles execute18 unchanged
legacy assertions each; the historical before/after delta uses frozen snapshots.
No test amendment or production test failure occurred. Complete author receipts
are in raw/author/validation.md and run1_summary.json.

The separate reviewer reproduced all30 profiles in a private WSL directory and
reviewed actual source/decoder/callback order/default passivity. Root policy
fixtures first demonstrated4failures/2errors against the absent literal route;
four exact route additions then passed7new+121prior methods. Reviewer independently
passed all128. These are script tests. No upload manifest or old test assertion
changed. Source review verifies exact-once pure decoder delivery beyond what
output equality alone can prove. Unreachable billion-call/sequence-wrap cases
remain source-reviewed, not privately seeded or claimed executed.

## Actual board Linux compilation and retained target bytes

Both checked profiles compiled exact96-file source
bf67d46da629cd4a59e14be62721b766070feac1c95d28b7a797f47d3a8172f6.
Default receipt63c8b798db3f4049bfb65df2bc578d27; Immediate
f611bac8fe694498939dc18691c70e7a. Both finalELFs are19,840bytes, SHA
4fa8171d133eca1e60a2329a380af6a8a7553ec29534796152f7b61c31dc419a.
All source bytes, three ELF forms and package per profile are retained. The
collector checks actual installed tool identities/CLI properties/imports; root
verify_targets.py independently rehashes every source/artifact and confirms all26
offline command results. See raw/root_target_verification.json.

Native32bytes; Runner9892;128x76-byte records9728. Conditional ordered-loader
model: payload16,245, peak17,128, free span245,016/largest245,012 in262,144.
This is offline capacity arithmetic, not measured loaded RAM. Startup remains
passive with a false grant, empty loop hook and no unrelated owner/transport/
allocator relocation. The source and target audit identifies every retained
initialization/reference path, rather than treating compiler exit0 as acceptance.

## Retained corrections and physical limits

The first target was superseded by the pre-test ordering correction. A race while
writing the clarified contract left the second source receipt with its older
contract hash; second_clarified_contract_binding.json explicitly binds unchanged
source to the actual later contract, before independent freeze. Original receipts
remain. Reviewer initial newline assumption failed and was corrected using actual
LF bytes; the failed verifier is retained. Root administrative reads also tried
two nonexistent summary filenames before listing actual artifacts; no evidence
or source was replaced. Initial policy red failures remain preserved.

The board still runs frozen D1042bd817c4. No physical ADC/button stimulus, divider,
settling, START/BOTH distinction, oscillator, readout, long-held gesture/display
composition, full-app800us or gate is established by this work. Production windows
remain unconfigured; SC-A remains unresolved. See bench/ui/README.md, the contract,
raw receipts and the scoped review for the exact acceptance boundary.
