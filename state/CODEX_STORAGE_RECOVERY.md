# Storage recovery - 25 September 2026

RECOVERED: exact final D185 test/review bytes are now in Git-owned evidence paths
listed in analysis/P7_current_app_compile_validation.md. The durable_final
checkpoint is historical; its later test receipts pass27+7methods and separate
review94fff07d has no open findings. Preserve three failed zero-byte Windows
receipts. WSL backup: /home/ubuntu/sumox-d185-recovery-20260925/ (17688B).

Cleanup92738412 saved174.38MiB by lossless compression; C: observed about2GiBfree.
The seven rejected npx folder deletions join all prior excluded cleanup paths;
see STORAGE_LOG.md. Do not retry deletion through another method. Free-space
fluctuations beyond measured allocation savings have an unproven external cause.

D185 bench (6d9e48f8) and MATCH (1fcc7d57) target compilations now passed; both
owners are consumed. Read the current CODEX_HANDOFF.md next action. Last upload
D184 completed with the isolated inert image halted. Default allocation deficit,
full-app IO fault, physical/human gates remain open; no job is running.
