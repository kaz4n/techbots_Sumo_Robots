# Independent D136 private oracle freeze

Prepared from adopted D136 including its public pure decode_cue interface,
adopted D135 wire semantics, and the unchanged D073/D074 CSV validator schema.
No future companion implementation or new public test body was read. This is a
separate same-model reviewer reusing prior P4/D134/design context, not a fresh
phase-gate reviewer or a cross-model review. No probes have been executed.

Nineteen unittest methods freeze independent expectations for: ten distinct
synthetic M1 passes; inclusive historical timing bounds; valid late receipts;
explicit HANDOVER_FAILED with a superficially correct state; M0 versus declared
hardware-origin eligibility; zero/wrap/common-anchor contradictions; every legal
nonpassing disposition; missing/late GO and owner contradictions; adjacency and
single-candidate grammar; selected phase/cause/side/front cases; historical
centering thresholds; invalid source including empty cohorts; restricted config
literal spellings and disabled modes; missing/mismatched source declarations;
loss and duplicate triples; same-size restored-mtime bound-reread mutation;
exact report/schema/path/CLI semantics; typed public decoder boundaries; and
nonadjacent receipts/invalid-clock diagnostic terminals. The public author owns
the exhaustive uint16 metadata table; these selected cases do not copy it.

Fixture data is authored here from the unchanged CSV headers and literal wire
layouts. No producer output, sensor observation, physical run or current config
is used as ground truth. Frames deliberately carry no evidence of the cue;
decoding must use TIMING metadata. Even a hardware_reported declaration is
fabricated synthetic test input, explicitly labeled as such. Fixtures live only
inside TemporaryDirectory and are removed on success or failure.

run_private.py binds the private files and unchanged dependencies, requires the
coordinator's exact implementation SHA256, forbids subprocess/network access,
checks no retained input changed, preserves uniquely named compact JSON/text
receipts, and returns nonzero for failures/errors/skips or changed bindings.
It must run only after explicit coordinator authorization, with no board or
compiler access. The runner itself and probes have not been executed or imported.

Prepared command, not executed:
`TMPDIR=/dev/shm PYTHONDONTWRITEBYTECODE=1 python3 state/reviews/P5_abort_analysis_review_raw/run_private.py <repository-root> <unique-label> <implementation-sha256>`

The freeze JSON binds file bytes before implementation review/execution. Any
later harness correction must retain the original source, failing receipt and
independent adjudication; never alter a frozen expected result to fit production.
