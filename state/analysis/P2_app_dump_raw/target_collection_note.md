# Frozen-source versus concurrent-current-source observation

Initial default96c80701 collection passed every identity check. Initial MATCH
collection preserved a nonzero collector outcome because its additional
current_source_at_collection check was false: src/app/runtime.h and
src/app/runtime_inputs.cpp had changed concurrently. All85 frozen source hashes,
aggregate96c80701, three ELF and package hashes passed; remote inspection exited0.
The original MATCH audit.json retains current_source_at_collection=false.

The collector now separates that observation from completed-build acceptance:
the explicitly selected full source hash must match the checked compile receipt,
the locally frozen85-file source and the complete remote source enumeration.
A later worktree revision is reported without invalidating those completed
frozen artifacts. No remote re-collection, compile or artifact replacement was
needed. Each subsequently selected source requires its own complete matching
85-file snapshot before any collection and writes a different target directory.
