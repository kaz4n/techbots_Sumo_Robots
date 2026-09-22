# Observed environment — 2026-09-22 Asia/Dubai

Read-only discovery before code edits: Get-Date, Get-Location, rg --files --hidden,
ancestor AGENTS scan, git status, Get-Command, version commands, WSL inventory.
Initial git status exited 128 (not a repository); no parent repository. Thirty
supplied files reviewed, secret-pattern scan found no credential material.
Baseline `52b935e` established locally; no remote configured.

| Tool | Observed |
|---|---|
| OS / local clock | Windows 10.0.26200; 2026-09-22 17:00:46 +04:00 |
| Shell | PowerShell 7.6.6; Git Bash 5.2.37 |
| Windows Git / CMake / Python | 2.52.0.windows.1 / 4.2.1 / 3.13.11 |
| Windows SSH | OpenSSH 9.5p2, LibreSSL 3.8.2 |
| WSL Ubuntu | kernel 6.6.114.1-microsoft-standard-WSL2; working |
| WSL g++ / CMake / Python | 13.3.0 / 3.28.3 / 3.12.3 |
| WSL Git / SSH / rsync / Bash | 2.43.0 / 9.6p1 (OpenSSL 3.0.13) / 3.2.7 / 5.2.21 |
| adb / arduino-cli / ninja | not on checked Windows or WSL Ubuntu PATH |
| Codex | CLI 0.155.1; exec/review supported; native delegation 4 total slots |
| Network | HTTPS fetch of pinned doctest header and license succeeded |
| Disk | initially 1.66 GB free on C:; no large toolchain installation needed |

No private key/config contents inspected; no board connection attempted. Unknown
SSH target and attached devices are not evidence of successful access. Compilation
on the UNO Q, installed core/library inventory, boot options and upload remain
pending; research reports alone cannot certify installed versions. WSL invocation
from PowerShell: `wsl -d Ubuntu -- bash tools/test_host.sh` (cwd is translated).

User subsequently asked to continue software assuming hardware works and defer
checks; record assumptions as unverified and keep working on eligible P0 tasks.
