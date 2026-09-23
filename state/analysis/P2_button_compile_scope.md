# Button path compile-only probe

`tools/flash.sh bench/p2_button_compile --compile-only` retains the actual optional
A1 acquisition, raw-window decoder and Robot gesture admission for target checking.
Global objects are plain state; setup stores a function pointer, loop is empty,
and the retained exercise function is never called. There is no upload allowlist
entry. This probe is not the B6 physical UI bench and supplies no physical reading.

Production raw windows are deliberately unconfigured (D087/SC-A). Synthetic host
profiles test classification and ambiguity without approving a circuit. Actual
START/BOTH voltage identity, display, scheduling and hardware acceptance remain
pending. No motor-run permission or human phase pass follows from compilation.
