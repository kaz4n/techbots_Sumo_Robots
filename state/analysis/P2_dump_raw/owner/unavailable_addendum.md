# D090 unavailable request clarification

2026-09-23. The frozen contract addendum requires `request_unavailable` to forbid
starting a session. The initial owner did not inspect this flag. A check at the
beginning of `Transfer::start` now refuses it with `Phase::REFUSED` and
`Reason::CONTEXT`, before metadata reads, formatting or Port callbacks. The intent
remains consumed by the existing step logic, so clearing the flag cannot replay
the same token. This check applies to session start; it does not queue or restart
an active session.

Strict C++17 syntax check was rerun with the exact flags in implementation.md;
exit 0 and empty output are recorded in `syntax_unavailable_exit.txt` and
`syntax_unavailable.txt`. No tests, public API, header, config, build definitions
or other worker files were changed. This supersedes only the implementation hash
in the earlier source_review.json; the added block is four LF-only lines and the
start function remains below 60 lines. Behavior tests remain independently owned.
