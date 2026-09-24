# D154 upload wrapper design review

25 September 2026, Asia/Dubai. Separate read-only design review, with authority
to write only this note. Disposition: **PASS for host implementation and frozen
independent tests; no open material design finding.** No implementation, test,
CLI, board, upload, reset or capture was executed for this review.

Reviewed exact inputs:

- `analysis/P7_static_upload_contract.md`: SHA256
  `319ce137afbd32d1fe1486220d613eae06791fcd3007396e5f9c8761d3c5b95c`.
- `analysis/P7_static_startup_raw/upload_bindings.json`: SHA256
  `a31bca78bb619271e63a321173a68fca072e48bb22111ee20fc9f8c20d5e18fc`.

The contract uses stateless D153 support and frozen descriptor helpers without
altering their globals, instantiating Capture, or adding another framework.
Fixed argv/config/environment, raw selector versus flat payload, exclusive
attempt ownership, independent finalization and no automatic capture agree
with the retained route and guard notes. The explicit 180-second overall
admission/launch/wait budget and 120-second maximum child wait are distinct;
the additional bounded five-second reap does not establish target quiescence.

Sixteen of seventeen file pins were compared directly with retained upload,
include, selection and D153 binding records; all matched path, size and SHA256.
The raw BIN pin matches the D144 values in P7_static_upload_route.md. The three
directory sets agree with the corrected F165 receipt. Fourteen fixed absences
cover the stated overrides, include shadows and sketch metadata; absence of
the user hardware directory also excludes its platform.txt. /tmp/remoteocd
is separately admission-only, since the checked upload route creates it.

Native admission remains explicitly incomplete: the future coordinator must
bind reviewed HEAD/source and D144 identities, close index/builtin/metadata
initialization prerequisites, and identify the inert run before launch. F165
does not by itself prove CLI initialization purity. This is a retained boundary,
not permission supplied by this review or an implementation blocker.

Implementation acceptance still requires frozen spec-derived cases for late
deadline expiry before Popen, claim/fsync failure, timeout/unreaped completion,
malformed outcomes, every independent postcheck, original-fd finalization after
path drift, first-error retention and result-persistence failure. Passing those
tests will establish controlled host behavior only; code/receipt review and
the separate native admission remain necessary.
