# D190 first completed host execution: fixture isolation failure

The earlier120s invocation timed out with no observable completion. The exact
frozen command then executed62 methods in158.573s (175.994s outer), yielding
1failure/3errors, all in three ActionsContract methods. All147pins unchanged.
The failures reject fixture /home/arduino ownership before intended action paths.

Root controlled observation: actions oracle pwd module is not current imported
pwd (False); actual host UID1000 account is ubuntu. The driver loaded each
oracle inside mock.patch.dict(sys.modules, aliases), which restores the entire
module dictionary and removes pwd first imported by the actions oracle. Its
patches then affect an orphan module while the real helper imports a new pwd.
Separate fresh-context reviewer independently reached the same source cause.

Repair only the new projection-driver alias context: save/restore only explicit
private-oracle aliases, preserving unrelated stdlib imports. Add account-module
identity assertion. Original three oracles, all existing assertions, native
variants and helpers remain unchanged. Preserve this first completed receipt
and source in Git before repair; freeze repaired driver before execution.
No firmware upload/reset/MCUread or runtime proof follows.
