# D241 production static MATCH tooling

The one admitted compile tuple is ordinary app.ino, MATCH=1,
MOTORS_ALLOWED=1, all eight commissioning/probe macros explicitly zero,
`arduino:zephyr:unoq:link_mode=static,wait_linux_boot=no`.
The installed boards.txt menu keys and CLI platform specification define the
combined selection. The eventual properties query must match that exact FQBN,
static link mode, Immediate boot mode and all controlled recipe strings; it
cannot fall back to another tuple. Installed platform.txt adds `-immediate`
to both package recipes. The saved zephyr-sketch-tool source sets prelinked
0x02 and Immediate 0x04, hence the exact expected package flag is 0x06.

New compiler, policy, remote artifact collector, precompiled uploader and
deployer derive from reviewed D222/D227 source. Original tools stay unchanged.
Five checked policy snapshots, complete ELF/TLS/flat-body checks, source Git
identity, one compiler/query, descriptor observations, owners, subprocess
closure and all nine compile closing checks remain. Only the private package
header expectation changes from flag2 to flag6; the original validator source
is still hashed before execution. Flag2/4 or damaged body cannot qualify.

Compile entry point (local check, then separately admitted compile-only):

`python -I -B tools/compile_match_static.py --check-only --profile match --motors-allowed 1 --attempt TOKEN --reviewed-head FULL_HEAD`

Replace only --check-only with --execute for the one compiler attempt.
No upload is part of this compiler. Its raw parent is
state/analysis/P7_match_static_raw; source/attempt-derived owners cannot be
reused, including after failure. Compile-only needs no motor-run permission.

Future precompiled deployment uses:

`python -I -B tools/deploy_match_static.py --check-only --scope RELATIVE_JSON --reviewed-head FULL_HEAD`

The scope schema is match-static-app-deploy-v1. Request fields remain the D227
closed request shape with profile=match, motors_allowed=1,
mode=operational_match, startup=immediate and the exact D241 compile receipts.
The current full source/config must equal the compiled historical Git blobs.
This standalone path continues to refuse nondefault identified sessions.

Production qualification and authority use the existing match_deploy.py
functions unchanged, with the exact static/Immediate FQBN substituted in the
private module. The qualification schema remains
match-operation-qualification-v1: exact source/raw/package, installed runtime
and target bindings, reviewer/limitations, bounded evidence, and stand or ring
operation. The matching match-human-authorization-v1 must bind the whole
request and an actual STAND OK or RING OK, valid for at most one hour. The
existing production policy has no explicit phase-gate field; none is invented.
Compile or host fixtures cannot provide qualification or run permission.

Fresh-session production delivery uses the additive D240 derivative:

`python -I -B tools/run_match_identified_delivery.py --check-only --scope RELATIVE_JSON --reviewed-head FULL_HEAD`

Only this paired route admits stream ID1 and a positive uint64 session equal
to the run ID's first16 hex digits, present in the exact compiled config. It
requires the four existing native dump grants and production qualification.
On --execute it exclusively consumes the session-prefix owner, arms the
existing dump_match receiver, waits for connection, revalidates the claim,
then permits one existing qualified upload. Standalone deploy keeps refusing
those settings. Reset does not renew a session, and failure consumes it.
The complete generic version1 envelope/session/CRC/CSV validation is unchanged;
no synthetic recorder count or timing is imposed. First and secondary errors,
receiver cleanup and failed final-journal outcome remain available.

This is host/tooling preparation only. Current firmware/config/grants, physical
qualification, human gates and native run authority are unchanged. No native
command, upload, reset, cleanup or firmware change is made by this preparation.

Primary source evidence retained in the repository:
- `state/analysis/P2_bridge_dependency_raw/installed/core/boards.txt` (6101 bytes; SHA-256 `bd4f03904d8fe16bf845baf09d0435e79f5a46c6e6a4f445f3ee592994652b84`).
- `state/analysis/P2_bridge_dependency_raw/installed/core/platform.txt` (20947 bytes; SHA-256 `d4c824fceb2f4cf0057da4df3235d3aee195bbbd71f59a48d344c818fcd5e638`).
- `state/analysis/P2_bridge_dependency_raw/primary/arduino-cli/docs/platform-specification.md` (82144 bytes; SHA-256 `d05d619c2d70debe58f340ef5c3bb552b52e0c186d8dd9fdb90b6a4ee2be2624`).
- `state/analysis/P7_static_link_research_sources/zephyr-sketch-tool_main.go` (3521 bytes; SHA-256 `a4270be85f66b0f309a7c540917aa23820812bd04a5a6355863e70585aaabf4b`).

Relevant lines: boards54–61; CLI specification139–140; installed platform94–97 and164–165; sketch-tool76–84. These establish the selected options and header bits, not a completed current target compile.
