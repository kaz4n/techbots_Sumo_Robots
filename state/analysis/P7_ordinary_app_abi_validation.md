# Ordinary application ABI inspection evidence

26 September 2026. D209 is preparation for file-only inspection of the accepted
D208 ordinary static/default/MATCH0/MOTORS_ALLOWED0/probe0 artifacts. No ordinary
ABI observation or runtime result has been obtained by this task yet.

Adopted contract `P7_ordinary_app_abi_contract.md` is20543B/541710f0. Data-only
derivation `P7_ordinary_app_static_compile_raw/abi_derivation01.json` is54047B/
249a4209. Independent preparation review `../reviews/P7_ordinary_app_abi_preparation_review.md`
is7382B/5f40659e, FINAL PASS without a material finding.

The initial reader was43966B/fe64ceb3, with metadata-only receipt7618B/fb4c70a9.
Pre-execution source review found an incomplete/multiple-layout acceptance gap
and two fixture construction errors. All five initial subject/receipt/oracle/
fixture/freeze files are preserved under `abi_version01_preserved`; findings
and bounded adjudication are in `abi_preexecution_findings01.json`3620B/35f2ce6d.
No test failed at runtime: no subject or suite had been executed.

Current reader44449B/f816a523 changes only `_complete_layout`, rejecting
unavailable type placeholders and requiring one complete outer body ending at
the block boundary. Receipt8480B/4e8fb0a1 proves all other bytes unchanged.
The final privately projected reader remains12965B/7fb42d51. All seven
retained guard/CLI function bodies match D204 exactly. Twelve counted metadata
changes produce the16613B/c6d2fad3 intermediate; restoring the four semantic
spans reproduces it byte-for-byte. No production, configuration or historical
reader is modified. Those byte identities were sealed before source execution.

The fixed query covers13 layouts, six Runtime member offsets and47 enum values
with185 expression strings/92 markers across four bounded file-tool children.
The two ordinary object symbols remain hypotheses until freshly observed.
The parser requires unique aligned nonoverlapping objects inside initialized
BSS, valid window geometry, ordered complete answers and absent diagnostic
symbols. No old Runner, Trace or SETTLE coordinates enter this schema.

Independent revision02 fixtures correct bounded constant resolution and the
canonical-command positive fixture, and add the missing negative layout cases
without removing prior assertions. Oracle44414B/0a88018a, fixture54898B/ec2494c6
and freeze31050B/847d3831 were FINAL before renewed source review and execution.
The author did not inspect the subject. A pre-write author bookkeeping assertion
refusal, corrected to include mock assertions in the existing AST count, is
recorded in revisionreceipt2624B/fb32ef21; it was not a test or product failure.
The host driver3497B/1e50cb8e is exactly D204's682516a4 driver after three
metadata substitutions; independent review confirms retained limits, exclusive
owners, saved streams, pin closure and temporary-directory handling. No native
attempt has run yet. The360-second host outer ceiling is stricter than
the independent fixture's600-second maximum; both reviewers accept that choice.

## First host runs, independent final acceptance

Coordinator freeze30803B/0173a01c binds159 exact inputs. The scoped source
reviewers approved execution after the bounded fixes. Each suite ran once.

| Platform | Result | Inner / outer elapsed |
|---|---|---|
| Linux | 66 PASS, no skips | 52.686 /65.828 seconds |
| Windows | 64 PASS,2 explicitly covered skips | 7.423 /7.837 seconds |

The Windows symlink-privilege and Linux FIFO-race skips have the exact matching
Linux PASS outcomes. Both runs preserve every input and the coordinator freeze,
with no timeout or retry. Saved stderr hashes are533ae8bb (Linux) and9ab54cdb
(Windows). Raw records are `abi_first_linux01` and `abi_first_windows01`.
Host closure26889B/9b85a177 independently verifies all132 ordered outcomes and
saved stream hashes. The dedicated Windows temporary directory and scoped
UID1000 Linux `/dev/shm` inventories are empty. C: free space was6493216768B.
All first pre-execution findings and original versions remain retained.

An accepted file observation would still not establish ordinary loading,
runtime success, live RAM/stack, timing, hardware acceptance or a phase gate.
The ordinary loop has no terminal diagnostic publication: its reports and
native motor bookkeeping can change during reads, and FAULT can appear before
cleanup finishes. A later finite runtime scope must preserve those limitations.

Final source/host review8934B/f3e72aca is accepted at 2026-09-26T16:38:33.194692+04:00, with no open material finding. Fixed abi_native_scope01.json binds ten input roles; separate admission and a clean reviewed HEAD precede the one file-only attempt.

Separate admission review6585B/bd83b5ce FINAL PASS accepted at 2026-09-26T16:42:11.311676+04:00. Ten scope,159 coordinator and125 manifest bindings independently match. Reviewed scope3318B/e34576f4 admits only check-only then one file-only execute at clean HEAD; actual output/review remains pending.
