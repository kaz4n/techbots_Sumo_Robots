# D212 saved-file retrieval preparation review

FINAL PASS, 2026-09-26. Independent review of root-authored preparation using a same-model, reused context; this is neither human nor cross-model review. Only this review was written. No subject import, test, device call or retrieval was executed by the reviewer.

## Exact reviewed identities

Paths below are relative to `state/analysis/P7_ordinary_app_run_raw/` unless stated otherwise.

| Input | Bytes | SHA256 |
|---|---:|---|
| `retrieval01_readonly.py` | 4695 | `162d152d68deb596b524f953a377b222fec360e088bdd8b26d4a21091db271cc` |
| `retrieval01_intent.json` | 23840 | `68ff090a750c4ae6ae41e12e5c317f1ed2bb8bc0ae532d98f0c779f024b7bb30` |
| `native_actual_closing01.json` | 10473 | `c843482de7bd0105080fa7e9a8e1280ee21f142cad2ac78cc0567e93e0928cc4` |
| `native_inert_run01/result.json` | 59671 | `c41453c23373e7a24215acfff7e95d80b27e4a34eb4abddbe0d65a236293825f` |

All seven intent input byte/hash pins independently match current files. The contract remains FINAL02 `828b334235877131580618908cc164381a988f297c4e22235eb72e34fe200e75`.

## Preparation and evidence checks

The historical D207 reader is 4330 bytes / `c04b13aecadc1b10fa92a7c0293c7993d8ecf0cf13a140baf439998b9091a935`. Removing the first two assignment lines from each reader leaves exactly identical operational bytes, SHA256 `49494df4594ab7c176145c1f3ae1bc63e9c971b0b9f1e0da3e2b60431eca4e5f`. AST-literal extraction confirms the assignments remain EXPECTED then PINS. EXPECTED equals the completed native input identity, including boot `55c386b9-fe6d-4388-a7f4-1d91e0bb49d8`, arduino UID/GID1000 and Python3.13.5.

The 16 unique pins match the intent exactly. The two report pins derive directly from actual returned upload/capture envelopes, which match the saved transport stdout JSON. They total9625 bytes: upload1799 and capture7826. The remaining14 pins exactly match ordered capture reads7..20 and saved analysis snapshots, with paths under the current capture owner, totaling2610 bytes. Total retrieval payload is12235 bytes. No flash binaries or additional SRAM reads are requested. The native result records COMPLETED, one upload/one capture, null first error and empty closure/transport errors; the pinned root closing records all13 checks and380 stable inputs. This preparation review reconciles the retrieval subset and does not replace a full independent actual-result review.

The argv is exactly the historical six-element ADB invocation structure for board2629958581, using shell -T and `/usr/bin/python3 -I -B -c`. Shell-token parsing recovers the exact reviewed reader and unchanged compressed helper token. Decompressed helper bytes equal the retained33321-byte static_remote.py, SHA256 `8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8`. Windows argv measurement independently reproduces18059 UTF-16 units including NUL. The outer75-second timeout and remote60-second alarm remain unchanged.

The inherited helper retains descriptor-relative directory traversal, no-follow regular-file opening, bounded reads, pre/open/post identity checks and descriptor closure. The reader enforces exact length/hash for each file, repeats all16 reads before returning, checks complete before/after Linux identity and closes its root descriptor in finally. Its only outputs are the saved-file JSON/base64 packet. No MCU, reset, upload, compiler, privilege or credential operation is added.

## Admission and limits

`retrieved_inert_run01` is currently absent. PASS admits one invocation of this exact intent after enforcing the fresh exclusive local owner and unchanged input pins at use; preserve exact intent, stdout, stderr and packet bytes. A failure or mismatch requires separate adjudication, not automatic retry. The returned16-file packet and decoded ordinary outcomes remain unobserved at this seal. File consistency does not establish SRAM atomicity, execution continuity, completed cleanup, final inhibition, physical behavior, WCET or a phase gate.

The intent preserves root's data-only construction refusal caused by an initial assignment-order assumption. One reviewer audit likewise stopped on an incorrect assumption that native diagnostics was an empty list; inspecting its actual dictionary and checking its error arrays resolved that audit-only refusal. Neither involved product, evidence or test changes. No material finding remains. Writes stopped after this seal.
