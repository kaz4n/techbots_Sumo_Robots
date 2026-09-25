# Exact stale-scratch cleanup source review

Reviewer /root/app_trace_abi_scope, separate reused read-only same-model context.
Initial material finding in draft62607054: outer process-read disappearance was
not distinguished from a surviving PID with missing/unreadable metadata. Require
PID existence recheck, and repeat directory mode/owner/link identity before each
unlink/rmdir. These changes were made before any execution.

Final PASS, no open material finding: cleanup_remoteocd01.py
23ef85ae3c386cc76751eea0fb18a90148a6fe513e3e8c753d527c06efcbbe95,7873bytes.
PID failure73-78 rethrows for a surviving PID. Directory comparisons118/125 retain
device/inode/mode/UID/GID/nlink. Fixed full identity/boot and directory34/33,
three plain singly linked files, exact bytes/hashes and retained originals,
repeated process/use/identity/inventory checks bound the deletion. Only those
three relative basenames and the empty directory can be removed; no recursion.
Partial removed list and failures are retained; originals rehashed at closure.
Other-user FD visibility is limited and recorded; observations are not a lock.

Provenance: all three copies match D184's successful upload and current installed
originals. D184 preparation6b5df730 is bound by its original native inputs;
completed result e462f229 retained. Exact known sizes total2334244bytes. D189
refusal8ce6cae3 precedes uploaderclaim/nativeCLI; adapter writes already occurred.
No cleanup, tests, file edits or board operations performed by the reviewer.
