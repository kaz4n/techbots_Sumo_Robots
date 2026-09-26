# Current ordinary application: static compile preparation

26 September 2026. D208 advances the ordinary application after the accepted
D207 inhibited diagnostic. **Source, host and native compile-scope review passed; check-only and the
actual compilation remain pending.** No ordinary target artifact or runtime result is claimed.

The production sources, configuration, seventeen zero setup grants and probe-zero
default are unchanged. The new `tools/compile_ordinary_app_static.py` privately
adapts the existing guarded compiler for `app.ino`, static linking, default
startup and exactly `-DMATCH=0 -DMOTORS_ALLOWED=0`. It preserves the original
bootstrap, resource limits, exclusive ownership, one-query/one-compiler bounds,
artifact validators and independent closing checks.

The snapshot mapper and actual pinned `match_deploy.app_source_hash` agree on
`9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a`.
There are 105 checked source files, 104 staged destinations and 764405 source
bytes. The exact input manifest is the union of those 105 source names and
twenty required tool/contract names, totaling 125. The unmapped app `.gitkeep`
remains covered by the manifest. Actual local manifest admission passed without
creating a stage or native owner.

## Independent host evidence

The independent author froze contract-derived fixtures before inspecting or
executing the new subject. Review found two fixture construction defects before
the first run: inherited remote-case duplication and a fixture read inside the
subject no-I/O guard. The bounded revision preserves the original versions and
every assertion. The first Linux caller run then returned **78 PASS / 2 FAIL**:
two old diagnostic negatives had become identity replacements under the ordinary
two-flag profile. Independent review confirmed this fixture fault. Only those
two negative values were changed to the prohibited probe-enabled profile.
The failed result remains failed evidence; the product tool never changed.

Revision03 results, run serially with exclusive saved output owners:

| Suite | Linux | Windows |
|---|---:|---:|
| Caller/bootstrap/mapping | 80 PASS | 77 PASS, 3 skips |
| Remote/artifact/adapter | 55 PASS | 34 PASS, 21 skips |

Every Windows skipped test has the corresponding Linux pass. All 191 frozen
inputs remained unchanged; scoped Linux and Windows temporary directories were
empty at closure. The complete 33-method historical adapter coverage is included.
The root closing-summary script also had a syntax-only construction refusal
before any execution or file write; it was corrected without repeating a suite.

Final source/host reviews are
`../reviews/P7_ordinary_app_static_compile_source_review.md` and
`../reviews/P7_ordinary_app_static_compile_remote_review.md`. Exact raw outcomes,
preserved failures, fixture revisions and the closing receipt are under
`P7_ordinary_app_static_compile_raw/`.

## Prepared board operation

The separately reviewed two-call read-only admission passed: all 28 installed
pins, Arduino credentials and boot identity matched; no conflicting tool process
or new remote owner was found. Root/home free space was approximately 2.94/13.91 GB.
This observation does not replace the compiler's checks at use.

`native_scope01.json` binds fifteen evidence roles to one properties query
(60 seconds) and one serial compiler (720 seconds, five-second reap). Independent actual-admission review
`../reviews/P7_ordinary_app_static_compile_admission_review.md` passed. Clean
committed HEAD and successful local check-only must still precede execution. Upload, reset, MCU reads, installation and retry are
outside this scope. Existing firmware remains the accepted D207 diagnostic.

Any later compile acceptance establishes inhibited ordinary file artifacts and
structural layout only. Loading, live RAM/stack, ordinary runtime/WCET, native
UART ownership/rearm, physical sensors/motors and human gates remain separate.

The final Git byte audit found four inherited CRLF inputs whose index blobs had
been normalized to LF. Four exact-path attributes preserve their already-reviewed
working bytes in the new commit. Frozen oracle EOF bytes also remain exact.
Audit index_byte_audit02.json confirms 228 matching blobs and 191 unchanged pins;
no source, JSON value or assertion changed.
