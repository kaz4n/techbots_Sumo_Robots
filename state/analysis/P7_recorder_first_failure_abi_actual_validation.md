# D233 fresh file-only ABI actual validation

At collector43a9ae9f, localcheck returned0 in1.907s and one file-only invocation
returned0 in4.671s. Four installed offline readelf/GDB children returned0/reaped
without timeout or stderr. Twelve file checks, board identity and local closure
passed. All156 local pins match current/collector Git bytes. Source is29cb1e76,
historical compileHEADce4e6939; this observed closed compiled files only.

Actual ABI221717e2f45fa51a63a82def322e3c287047d9565b207ae1463142d674c0c7c2
contains9types/11windows/64fields. native_dump is216B at536950928, .data;
runner is164192B at536951144, .bss. FailureRecord is8B at offset205/address
536951133, observed from this exact ELF rather than assuming old padding.
Six aligned ranges total692B per status snapshot. Full loader263680B and
current sketch55376B remain mandatory before/after brackets for later capture.

Independent actual reviewe8f4f533 FINALPASS reconciles the ABI/raw queries.
Three data-only bindings were prepared once via the reviewed caller, specSHA
defe61a6562422753bde9e15ea7465a1d02aa9476ae3750042cc9fd3d7f9c120.
No new source/test/admission guard changed. Consume native_abi01; no rerun.

The file-only operation overlapped the TCP receiver under root's explicit
D051 scheduling decision. Passive MCU capture remains unperformed and waits
for delivery/receiver closure and its same-clean-HEAD check. No dynamic cause,
loaded image, delivery success, live timing, physical qualification or gate
is established by this compiled-file result.
