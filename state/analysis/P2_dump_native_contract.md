# D090 native port and inherited hook contract

Read P2_dump_native_audit.md and pinned installed artifacts. No stock Bridge/
Monitor/Serial calls and no RX parser. Same existing internal LPUART1->router
mon/write protocol; no external wiring or remote motion/reset path. Direct UART
operations use verified privileged Thread and exclusive ownership, checked device/
base/clock/config/IRQ/DMA context. Save/restore exact incoming PRIMASK; finite work.

begin is once-only and setup-only, requires all SetupGrant fields true. Refuse
before I/O on invalid grants/context; repeatedbegin refuses (never reinitialize).
The explicit caller grants are not hardware checks. Only setup may invoke installed
device_init on deferredLPUART1; audit positively shows unbounded TEACK/REACK waits.
Record this initialization limitation; no lazy runtime init or boundedsetup claim.
Configure/check exact PG13 inputpulldown for both normal/Immediate startup, checked
GPIO API status. Disable stock RX/TX interrupts/DMA under exclusivegrant; do not
use retrying atomic helpers at runtime. Check live register state beforeeveryTX.
No Bridge.begin worker may exist. Begin may succeed with LinuxreadyLOW; ready()
samples exactPG13/status eachcall and prevents writes unlessHIGH. No boot-time
readiness assumption. Claim ownership only under actual setup integration grants.

One pending packet encodes exactly93 02 A9 'mon/write' 91 D9 n followed bynASCII
bytes (1..DUMP_PAYLOAD_BYTES<=64). FixedD9 length form valid for all lengths.
Port.write returns PENDING0 while packet/TCpending; offered bytes/count must stay
identical until wholepacket completes. It returns PROGRESS/n only after full
packet submitted and a bounded TC observation. There is no Linux delivery ACK.
Each call tests TXE and stores atmostDUMP_UART_STEP_BYTES8 bytes without waiting;
stop immediately whenTXELOW. Check current ready/device/register context and
DUMP_UART_STEP_US80 deadline plus fixed iteration cap. Whole pendingpacket deadline
DUMP_UART_PACKET_MS100, equalityfails; time checks wrap-safe. Native errorsreturn
ERROR0. Deadlinefailures never fabricate progress. Successfulpacket clearspending
state for nextslice. Wrong count/data/ASCII/invalidcontext fails without newpayload.

Port.cancel must stop further submission and latchPOISONED; discardpendingbuffer.
Under stillvalid exclusive context, clearUART UE/TE and verify disabled readback
(finite, noACKwait). Do not issue TXFRQ: RM0456Rev6 documents it only in FIFO mode,
whereas this installed route has FIFO disabled. UE disable stops prescalers and
outputs/discards active operations; it is not a complete-packet/remote flush ACK.
If safecontext/ownership is
lost, do not write potentiallyforeignregisters; stillpoison/refusefuturecalls.
Bytesalreadyphysicallyshifted cannot be recalled; cancellation cannot claim zero
nonIDLEelectrical activity or completeframing. No finish/retry outsideIDLE. Any
partial packet may corrupt router's continuousdecoder. Rebooting MCU alone does
NOT prove decoder recovery; Linuxrouterrestart may resetMCU. No automatic recovery
or daemon restart. New begin on sameinstance isforbidden; physicaldeployment must
establish cleanframing before newowner. This remains a runtimequalificationlimit.

Implement separate strong C++ void __loopHook() in a .cpp including noArduino/
RouterBridgeheader. Emptyfinitebody removes inherited Bridgeupdate/mutex from
applicationloops. TargetELF must prove strongT exactbody/mainrelocation and audit
constructors/staticthreads; source alone insufficient. Preserve stockprovenance,
no installedcore edit. Sharedsketchhasheschange and needfreshreview beforeupload.

Host native tests cover everygrant, readinessstatus, register/IRQ/DMA/context/
PRIMASK path, exactwirebytes/79max, partial/PENDING/TC/timeout/cancel/poison, noRX/
stockAPI calls and invalidreentry. Actualcompile-only target proves API/layout/
stronghook linkage; bareboard synthetic runtime only after separate review and
identifiedinert run scope. Fulltick800us, independentclockSC-AJ, actualUART/RAM/
Linuxloss/cleanup and physicalB8 remainunproved. No motorupload/run/humangate.
