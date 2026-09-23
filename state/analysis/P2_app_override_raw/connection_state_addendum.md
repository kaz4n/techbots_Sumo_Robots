# Correction to the connection-state scope label

The original connection_state.json is preserved byte-for-byte. Its scope string
describes intended operations but incorrectly says "no ... server restart".
The actual stderr records an automatic local ADB server restart because server
protocol40 did not match client41. Only `adb -s 2629958581 get-state` was requested;
it exited0 and reported `device`. There was no explicit server-restart command,
board reset, MCU operation or upload. This is transport presence evidence only.
No further board/network operation is being started during the requested pause.
