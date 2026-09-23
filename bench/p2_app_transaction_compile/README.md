# D095 compile-only application transaction probe

`python tools/board_tool.py flash bench/p2_app_transaction_compile --compile-only`
builds the real owner on board Linux. There is no upload allowlist entry. Setup
stores a function pointer, loop is empty, and global construction is passive.

The uncalled exercise retains app::Transaction, actual Robot, native MotorGate
including terminal halt, and AttemptRecorder. App support is staged beneath
src/app; the .ino stays at the staging root. Host substitutes and exact target
source/ELF inspection are separate evidence. No sensor read, motor operation,
scheduler runtime, loaded-memory measurement or physical timing is established.
