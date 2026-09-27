# SumoX-26 robot firmware

Arduino UNO Q firmware and commissioning tools for the 3 kg autonomous sumo
robot competing on 3 October 2026 in Dubai.

**Continuing the project? Start with [HANDOFF.md](HANDOFF.md), then read
[AGENTS.md](AGENTS.md).** The handoff contains the current code checkpoint,
verified tests and board builds, operating limits, commands and next actions.

As of 27 September, software preparation and the latest board compilation checks
are accepted within their recorded scopes. The latest hardware report is UNO Q
only. The assembled robot, physical measurements and human phase gates remain
unaccepted; this is not an operator-ready release.

## Repository map

| Path | Purpose |
|---|---|
| [HANDOFF.md](HANDOFF.md) | Current continuation snapshot for any engineer or agent |
| [docs/PROJECT_STATUS.md](docs/PROJECT_STATUS.md) | Short project status |
| `src/core/` | Hardware-independent C++17 robot behavior |
| `src/hal/` and `src/app/` | UNO Q interfaces, scheduler and application services |
| `src/config.h` | Tunables, build profiles and setup declarations |
| `bench/`, `host/`, `tests/` | Commissioning sketches and host tests |
| [tools/README.md](tools/README.md) | Guarded build, deployment, capture and analysis tools |
| [docs/PLAN.md](docs/PLAN.md) | Scope, schedule, acceptance metrics and phase gates |
| [docs/HARDWARE.md](docs/HARDWARE.md) | Wiring proposals, electrical constraints and hardware qualification |
| [docs/BEHAVIOR.md](docs/BEHAVIOR.md) | Strategy, state machine and safety behavior |
| [docs/RUNBOOK.md](docs/RUNBOOK.md) | Prepared competition operating procedures |
| [state/PROGRESS.md](state/PROGRESS.md) | Authoritative phase and append-only progress registry |
| `state/analysis/`, `state/reviews/` | Original evidence, contracts and independent reviews |

## Continuing safely

Use [the common resume instructions](docs/prompts/RESUME.md) or
[the Codex resume instructions](docs/prompts/CODEX_RESUME.md).
Preserve evidence and user edits. Compile-only success is not permission to
upload or run motors. Every motor-capable run needs specific human authorization;
phase gates are written by the human after actual acceptance.

Host checks use CMake/CTest on Ubuntu WSL. The handoff provides serial commands
for constrained machines. Read the relevant tool contract before board work;
old diagnostic attempts must not be rerun.
