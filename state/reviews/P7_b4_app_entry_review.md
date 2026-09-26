# D217 B4 entry source, host and conditional native admission review

FINAL PASS, 2026-09-26. Separate reviewer using the same model and reused project context; not human or cross-model review. This review used source/AST, exact-byte derivations and saved receipts only. The reviewer did not import or execute the subject, run tests, or contact the board. No material finding remains open.

## Exact reviewed identities

Paths below are relative to `state/analysis/P7_b4_app_compile_raw/` unless stated otherwise. Sizes are bytes; hashes are SHA-256.

| Evidence | Bytes | SHA-256 |
|---|---:|---|
| `../P7_b4_app_entry_contract.md` | 7264 | bcc3072ccb1a219c3cf70ab92ce78d6e140fb4b619b2a370fc56d112a6daa543 |
| `entry_binding01.json` | 78168 | fb2ab19d0cd0337f7d74a9578eee58d2e0029bf8a45ad6851a9ddbf558c79d55 |
| `inspect_static_entry.py` | 18983 | b21582816f26b3dbc7e2ca961d186840aed5606ee50b3426f9c5187fa00362bc |
| `entry_derivation01.json` | 31050 | 2bc2cd7d2e20582e7c0ae3d8eba10fd95230f79ed333ac7615b39503fc21cf81 |
| repository `tests/tooling/test_b4_app_entry.py` | 25045 | a7d401cec037bdac0c70b897bb650791d1c71d2466870790f91b77a057d8c972 |
| `entry_oracle02.json` | 8469 | 2a5334f7e99e2b0e114cd5b56ead60d70281499fa8d17f5f101ffe237a5f2b81 |
| `entry_oracle_repair02.json` | 2548 | 649275e86775b4b000edeebde969c2c0acb4b3aabf54487bb39f4668aa61031c |
| `entry_coordinator_freeze02.json` | 26598 | 68628d44281b341849021edddf1a7eb1cdaf9a2524aaab1d76ec8eab454146c4 |
| `entry_host_closing01.json` | 5595 | b29e8d7ce7f51641ffa95749efdaae749f3b7834084fa311725635ae852531c2 |
| `entry_native_scope01.json` | 6328 | 4b0a7303a263dcaa6f0d68e7c156ee907352861c3727a83581ed20b2819a278f |
| `entry_native_driver01.py` | 5165 | 730e160444ee0436b18abf0944fac8a4c9745b096c3f0cb87035aba5bb134af5 |

## Source, binding and fixture findings

The 155 derivation inputs match. Reversing the ten declared wrapper assignments, introductory comments and two private module labels restores the accepted D210 wrapper byte-for-byte. Eleven top-level guard/CLI bodies are exact; `load_reader` differs only in those private labels. The complete D188/D209/D215/D217 reader projection was reconstructed as data, including each counted substitution and intermediate identity; its output is 13226 bytes / 5df04ffc6c532d236006bb67bfa772493d8b2dc165b5523e4777300a04f0bba9. The nine parser metadata substitutions produce 14256 bytes / dd011caad902b86cc6e47fded3be1695e4a96f84581e6a654acf38a2c96a1bfc. Relative to accepted D210, eight parser functions are exact, `queries` changes the build path, and `initializer` changes the three current section-address contexts. Guarded private composition retains current B4 source/artifact validation, checked file lifecycle, error precedence and closing behavior; historical main functions are not invoked.

All 2037 fresh D215 symbol rows were reconciled, including the hexadecimal Runtime size and unnamed row zero. The 64 selected nonoverlapping groups, 77 FUNC aliases, startup bounds and 10488 selected bytes match the binding. The only selected size changes from D210 are Robot construction 1440 to 1484, RobotResult construction 192 to 208, Transaction::applyDecision 288 to 292, and MotorGate::apply 248 to 252. All 13 constructor pairs and local/weak classifications remain explicit. The 129 expressions are exactly 64 marker/disassembly pairs and the end marker; no query expansion was introduced.

The eight focused methods meaningfully exercise complete positive packets, all declared body/projection identities, current composition, fresh census, changed sizes/missing aliases/incomplete coverage, all six initializer bounds and invalid pointer cases, current B4 admission versus stale ordinary/M1/wrong-profile data, and stale inputs rejected before private execution. Retained lifecycle algorithms are supported by exact historical body identity rather than a repeated historical campaign.

The original Linux invocation failed in fixture setup before any test method: its projection helper compared dictionary identities with the binding's two-item list identities. The original oracle/test and zero-test failure remain preserved. Revision02 adds only strict normalization of these two identity representations and uses it at the two existing comparisons. Count, before/after identity and every test assertion remain enforced. The complete 19116-byte test class is unchanged (153d9bb4d15ba4bb9ebe375a3a043ed7be28aa539341e0664c8d52532eb866c4). This was a fixture repair, with no product change. Original Windows execution was appropriately not repeated against the known setup defect.

## Saved host closure

The corrected Linux run passed all eight methods in 9.506 seconds internally / 19.9667824 seconds externally. Corrected Windows passed the same eight methods in 1.317 / 1.6802502 seconds. No skip, timeout, failure or error occurred in either corrected run. Both used isolated Python with bytecode disabled and a 360-second bound. The reviewer reconciled all 16 ordered outcomes, all 12 saved files covering the original failure and corrected runs, and all 169 current coordinator pins. Both corrected receipts report unchanged pins/freeze and empty stdout. Windows temporary ownership is retained empty; no independent Linux remnant inventory is claimed.

The host01 and native01 drivers are exact counted metadata derivatives of the accepted D215 drivers. Host02 changes only the coordinator filename and platform receipt suffix; its 3497 bytes hash to a587a9f77d76b234c5a9b1378f204b55525bb170105cd1c360b3e2efccd831c9. Native01 retains isolated check/execute, earliest-error reporting, exact outer streams, three independently attempted closing checks and exclusive receipt creation after child exit. Its retained `d217-abi-native-invocations-v1` schema label is cosmetic: the actual launcher, owner and prerequisite paths are all the reviewed entry paths.

## Conditional admission of the concrete native scope

All 15 scope-role file pins match. The scope binds accepted D214 M0/B4 artifacts and D215 ABI evidence, the exact current source profile and the corrected oracle/freeze. The local `native_entry_static01` owner and `entry_native_invocations01.json` were absent at review. Remote absence remains a required use-time observation, not a fact manufactured by this review.

Admit exactly one check-only followed, only on success, by one execution of the reviewed driver after the root adds this FINAL review, scope and all required inputs to the prerequisite union, verifies committed byte identities and a clean reviewed HEAD, and holds other writes through closure. Check/execute outer bounds are 120/500 seconds. The sole file-only transport retains four children, 60 seconds per child, 5-second reap, 1 MiB per stream, 400-second transport, 8 MiB reply, 128 MiB local free-space admission and 30000 UTF-16 command units. Its prospective 13785-byte program hashes to b440eede7e9ec6bc601256ff1253b6bb7fdf69e8e15346dfa53dcbb6d3e0afb4 and fits 5457 units including NUL. Embedded current identity/resource/remote-absence and 12 exact file checks precede use; 13 remote closing checks plus local closure remain required. No separate duplicate board observer is needed for this inherited boundary. No compiler, upload, reset, MCU read, privilege, remote owner creation or retry is admitted.

This is source/host acceptance and conditional file-only admission, not actual instruction acceptance. Expected initializer bytes at the fresh address are still unobserved until the native result. The selected ranges are not a closed B4 call graph; unselected stand/interior callees remain source/host evidence. Constructor-symbol absence does not prove absent construction. The BSS zero interval must remain distinct from its larger allocated section. No physical inhibition, firmware runtime success, retained-RAM capture, atomic coherence, WCET, free runtime RAM or phase gate follows. Actual native streams, instructions and closure require their own subsequent review.
