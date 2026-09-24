# D146 TLS collection composition review

2026-09-25 Asia/Dubai. Separate fresh-context, same-model source review.
Disposition: **PASS for the stated one-shot diagnostic; no open material findings.**
This is review closure, not coordinator GO or evidence of an executed collection.

Scope: `P7_static_tls_collection_plan.md`, `P7_static_tls_raw/collect_existing.py`
and `read_existing.py`, with the exact reused D143 functions inspected. Read the
current AGENTS, P7 progress/prompt, schedule and D143-D145 decisions. September25
is before code freeze; pending physical evidence and human gates stay pending.
No new code was executed/imported, no board command issued, and no file outside
this review was written. No unrelated production test matrix was required for
this literal, bounded diagnostic composition.

## Exact reviewed bytes and observations

- Collector SHA256: `2443cedc54e6df3f11249780fb7fb5a787612ea1dc88ad0a8d563fc404d8d31c`.
- Remote composition: `48ca3cdf0ef2eda317ceb58cd841ee53fa21ff92336abfd2212005cc6b4f8b6e`.
- Frozen runner/helper match `983e86d7eb68f437c50b4b790e96ca4520e092abe53e4d29e8ffe1a97502b208`
  and `8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8`.
- Independently hashed all17 original runner pins: zero mismatches. Historical
  receipts0001/0009/0021 match the three literal hashes in the collector.
- The pinned metadata independently confirms finalELF170616B/5cc2dfde,
  map666298B/15da1417 and debug/tempELF1764708B each with identical0f7f2825
  content hashes but distinct file identities. `observed/` is currently absent.
- D144's original result still reads FAILED/layout, onequery/onecompile,
  with the original nonzero layout rejection. Its consumed GO is not reused.

## Scope and failure analysis

The collector captures and hash-checks runner bytes before module execution;
the frozen entrypoint is not called. It verifies the original17 pins, uses the
existing source/stage checks, binds the three historical receipts, and requires
the exact ADB executable hash, serial and process-local transport settings.
The fixed launcher still must verify the captured collector hash before execution
as stated in the plan. This review does not cover an unspecified replacement
launcher or invocation that changes the reviewed bytes.

Exactly one `Probe.dispatch` invokes `python3 -I -B` through the existing quoted
ADB adapter. The inherited30000UTF16 command bound applies before transport;
the command receipt is created first. Both remote compositions are hash-bound.
The imported helper's entrypoint is not called. Its directory/file routines use
read-only descriptors, no-follow/nonregular rejection, file identity/hash checks
and directory/boot checks. The new call graph invokes no remote writer, subprocess,
compiler, upload, reset or inferior. Importing definitions that include claim
creation does not call those definitions.

All eight original artifacts and the claimed directories are checked around the
read. Loader39d4a4fd is mandatory. Assembly and optional fixed object are rechecked;
debug/temp records must equal their original records, and aliasing is accepted
only for identical hashes. The optional object path cannot be supplied by map
text. Its substring gate only admits reading that fixed candidate; actual linked
input provenance remains for the planned map/object inspection. Collection status
must not be interpreted as proving that object was linked.

Remote file bounds,2MiB response bound, canonical base64 and bounded zlib decoding
with EOF/trailing-data rejection limit framing and expansion. Length/hash checks
bind decoded bytes. The transport receipt retains returned stdout/stderr or
exception output before semantic checks. The first observation failure remains
primary through independent local postchecks; READ_FAILED records it where the
local filesystem permits. A timeout remains failure/unknown, with no retry.

The destination requires checked ancestry and absence, followed by exclusive
directory creation. Inputs, decoded files and result use exclusive creation;
decoded files are published only after response and local checks pass. If later
publication fails, no successful result is produced and the command receipt
still holds the payload; launcher failure evidence must be retained. These are
ordinary filesystem failure limits, not grounds to repeat the read.

Next: coordinator adoption and exact hash-bound one-shot invocation, retaining
its launcher/command results. Then analyze actual returned bytes. No frozen
validator/oracle, firmware policy, D144 negative evidence, runtime qualification,
physical acceptance or gate changes follow from this review.
