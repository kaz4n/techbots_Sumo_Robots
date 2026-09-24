<!-- Reviews the proposed D141 static/M0 compile-only artifact contract. -->
<!-- Preserves the initial findings and separates draft closure from execution authority. -->
<!-- Checked by read-only source comparison and exact Git/worktree byte hashes. -->
# D141 draft contract review

2026-09-24T23:58:14+04:00. Separate fresh-context same-model reviewer; this is
neither a cross-model review nor a human gate. The bounded revision closes both
initial MAJOR findings. No open BLOCKER, MAJOR or MINOR was found in this draft
scope; this disposition does not adopt D141 or authorize implementation/execution.

## Exact reviewed drafts

Path: `state/analysis/P7_static_link_probe_contract.md`.

| Draft | Exact byte count | SHA-256 |
|---|---:|---|
| Initial Git blob, `git show 6e6fe21c:state/analysis/P7_static_link_probe_contract.md` | 8435 | `7bcb1bd261ff01ed6ea132f3ecaa7bb0b0c558123e17f51acc3ba601cbb4f613` |
| Revised working file | 9493 | `4968e454de3aff35b4cdfd2341ee0d5f498483f4346a0c4c9ee7aa4e7e227d5d` |

Hashes were computed from raw subprocess/Git bytes and `Path.read_bytes()`,
without newline conversion. The bounded diff changes only the two areas below.

## Findings and disposition

1. **MAJOR, executable identity and relocation acceptance - CLOSED.** Initial
   lines 75-94 omitted the explicit ARM ELF32 ET_EXEC/no-runtime-relocation
   acceptance required by the D140 review at lines 110-114. Revised lines 79-94
   now require little-endian ARM ELF32 ET_EXEC, frozen ABI flags, rejection of
   runtime relocations, separately classified diagnostic relocations and a
   frozen named-section placement policy rejecting unexpected TLS/GOT/dynamic
   sections. Lines 125-128 require corresponding rejection controls.
2. **MAJOR, stale artifact acceptance - CLOSED.** Initial lines 24-25, 45-46 and
   70-100 did not explicitly exclude preexisting artifacts despite the D140
   review at lines 107-110. Revised lines 24-29 require exclusive new output/build
   directories, absent destinations and failure for missing, empty, stale or
   unbound outputs despite exit zero. Lines 126-128 require an otherwise-valid
   old BIN/ZSK negative fixture and rejection before compilation or validation.

## Remaining prerequisites and evidence boundary

Exact ABI flags, permitted section names/placement, complete static property and
command literals, fixed artifact paths and pin manifests must still be settled
and reviewed against the pinned sources. The public interfaces must be fixed
before a separate author freezes independent synthetic policy/artifact tests
without reading the implementation. Their absence is acknowledged pending work,
not a finding or permission to execute. The frozen tests, unchanged dynamic
admission/reference bytes and exact new code still require separate review before
any properties query or compiler invocation and its explicit scoped authorization.

The inert default/M0 one-source boundary, single compiler/stop rule, read-only
stage reuse and prohibition on upload/reset remain intact. D139's 592-byte
dynamic deficit remains unresolved. This review establishes no static artifact
fit, deployment, live memory, timing, hardware acceptance or phase gate.

Review actions were local reads, the bounded Git diff and raw-byte hashing; the
only write is this review file. No build, board command, download, deletion or
implementation execution occurred, and no contract, ledger or production file
was edited by the reviewer.
