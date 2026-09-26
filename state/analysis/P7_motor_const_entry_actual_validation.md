# D205 actual emitted instruction evidence

The single file-only attempt at clean HEAD
`0a3f2b9ef755fde08086fc01c728a96c339e8e19` completed on 26 September 2026,
13:47:18.834-13:47:20.419 Dubai. Check-only and execute returned zero. One
5005-unit transport ran four successful, reaped children; all 13 remote and
the local closing checks passed, with no first error. No MCU access or firmware
operation occurred. D201 remains the latest flashed image; this owner is consumed.

| File in P7_motor_const_compile_raw/native_entry_static01 | Bytes | SHA256 |
|---|---:|---|
| inputs.json | 23279 | a420e45658fc292599e85bd6624348f5cf880999cc82d1bd1cfe52e733d247af |
| result.json | 423604 | 6700e974d75a99d3b82d044bb026cb43c060730b4f94fad16c007d4702d944e2 |
| entry.json | 10875 | b80c8ce88d199de4538c465ab9c858ca69f2c635a5630a9b731297d9aa7cf2d5 |
| local_result.json | 277 | 495c501ded117bb53e09e6e64eba56403b66469a41bc7b8c376a5d7aa90600e9 |

Root closing `entry_native_closing01.json`, 4089 bytes,
SHA25682abafa93d94356450b165f444541769bb7bca29c4de693f246cc82f8eb79484,
independently verifies 268 coordinator, 13 scope and 151 runtime local pins,
exact commands, decoded stream lengths/hashes, ordered remote closure and all
32 range blocks. The eight native files total889913 bytes; C: had8238292992
free bytes at closure. Preserve original streams; no duplicate ELF was downloaded.

The observation covers 32 ranges, 34 symbol aliases and3834 selected file bytes.
Its1429 disassembly rows include decoded literal pools, so they are not an
instruction-execution count. Fresh `.init_array` at0x08116258 contains05011008,
pointing to0x08100105; its end is0x0811625c and other checked bounds0x08116258.

`candidatePeriod` at0x08110c90 selects250 for timer0,3200 for timers1/2 and
zero for other inputs, without the former division dispatch. `timerValid`
retains its indirect live rate getter at0x081111f6 and compares the returned
64-bit rate with2,500,000 or32,000,000. Its timer register observations and
candidate-period call remain. This establishes emission of the intended
constant selections; it does not inspect all loader/getter arithmetic or
measure oscillator frequency.

The selected `bankValid`, `writePwm` and `mapChannel` bodies retain bank checks,
pre/post enable-low validation, bounded alias/channel matching and the
MOTORS_ALLOWED0 nonzero-pulse rejection. `settle` retains the150us deadline,
4096-poll bound, three fresh update flags, repeated bank validation and all
failure publications. Its successful path still requires the final elapsed
check. No timeout, safety bound, pin or grant was relaxed.

`publishSettle` writes current fields before the presence flag, and preserves
the first failure only when its flag was unset. The separate scalar stores
do not prove atomic or coherent multi-field observation. Startup, constructor
and Runner semantics are covered by the separate actual review. The retained
global division stub alone says nothing about calls on the optimized path.

These are file-emission findings only. Runtime benefit, successful setup,
WCET, live RAM, physical acceptance and human phase gates remain unproved.
A fresh, separately reviewed inhibited runtime attempt must bind these
current artifacts and ABI; historical runtime owners cannot be reused.
