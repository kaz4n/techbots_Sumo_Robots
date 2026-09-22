# Start this kit in Codex

1. Extract this archive and open the `sumox26-agent-kit` directory as your project. Keep hidden directories such as `.claude/`.
2. Read `docs/CODEX_HANDOFF_REVIEW.md` for the migration findings and engineering conflicts.
3. Open Codex against this project with permission to edit project files and run development commands. Retain normal approval controls. Board access and hardware-run approvals remain separate.
4. Paste the complete contents of `docs/prompts/CODEX_KICKOFF.md` into Codex. Alternatively, instruct Codex: "Read docs/prompts/CODEX_KICKOFF.md in full and execute it as my project instruction."

Use this Codex kickoff instead of the original Claude-specific kickoff. All original files are retained unchanged for provenance. The prompt instructs Codex to append the authorized workflow decision and a minimal persistent AGENTS.md handoff, then implement the active phase.

This is still a planning kit, not prebuilt firmware or an installed toolchain. A fresh run starts at P0. Real hardware checks, independent review, and human phase approval are required before subsequent phases can be claimed complete.
