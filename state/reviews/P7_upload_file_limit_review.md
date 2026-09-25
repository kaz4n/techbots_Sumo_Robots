# Additive upload file-limit correction review

25 September 2026, Asia/Dubai. Separate same-model review reusing D154-D156
context. Design review only at this checkpoint; no implementation/test/native
execution by reviewer. Reviewer owns only this review note.

Contract SHA256
`8b31b281a69fbf4c54794b99965b559d780b4138093ffcd56ee72d4aab05871d`.
**Design PASS for host implementation/testing; no material design finding.**

An explicit upload_loader entry and per-instance preexec callback isolate the
2303728B file cap from legacy upload and frozen D153. A shared small runner
avoids module copies and global rebinding. The source-specific cap admits the
largest authorized copy while both diagnostic streams still require <1048576B
for acceptance. The contract explicitly permits larger transient stream files;
it does not incorrectly retain a physical1MiB ceiling claim.

Independent companion tests must exercise all inherited cases through the new
entry, adapting only its invocation and two new-API preexec expectations while
leaving original tests unchanged. New callback/cap, both stream boundaries and
support-global stability remain necessary. Four real Linux copy tests already
establish the loader/cap boundary; they do not validate this new wrapper wiring.

Original81668c79 source and every old oracle/receipt remain historical evidence.
Changing the uploader digest must fail D155's old source pin, and the legacy
entry keeps its prior behavior. No current output/run binding changes: consumed
run01 is not revived. Residue handling, fresh ownership and any later caller/run
selection remain separate. No cleanup, native operation or retry is authorized.

Actual source and frozen test receipts are pending; design PASS is not evidence
that the uploader correction has been implemented or executed successfully.
