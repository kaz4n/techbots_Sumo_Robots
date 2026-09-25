# D173 file-only diagnostic ABI observation

Scope: inspect the exact successful D172 active diagnostic files, existing loader
and installed file tools on ADB2629958581/UID1000/boot6d4aca1b. User bare-board
permission and D051 cover this read-only investigation. No upload, reset, target
connection, MCU read, recompilation, source/stage deletion or package installation.

Run inspect_active_abi.py once with Python-B and --execute after separate source
review. Its fresh native_abi01 directory owns the evidence; preserve failed output,
do not retry that ownership. Existing transport and child wait/reap code are
hash-bound and reused without modifying the consumed compilation profiles.

Exactly five file-reading children: installed readelf/GDB versions, final ELF
headers/sections/symbols, debug ELF diagnostic type layouts, and loader LLEXT layout.
GDB disables initialization/auto-load and function calls; no target/run command.
Each child has60s deadline/5s reap and1MiB per-stream output cap;400s outer bound.
Ephemeral board-side output files close automatically; no firmware is downloaded.
Verify25 pinned files before/after (22 D172 pins,2 tool pins,1 build-export copy),
stable file identity, board identity and117 local compilation inputs. Preserve raw
transport, actual child command/status/output and first failure independently of
postchecks. A hash/layout result is artifact evidence, not runtime qualification.

The existing D172 compile JSON supplies the exact dynamic motor_fault.ino recipe;
the query checks its build export against the verified output export hash. Do not
execute that recipe. Source enum/field definitions and actual ABI jointly inform
the later finite decoder; do not infer ARM layout from host sizes.
