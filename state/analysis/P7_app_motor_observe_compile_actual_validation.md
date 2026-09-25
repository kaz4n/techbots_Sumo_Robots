# D193 actual inhibited observation compilation

The single compile-only attempt succeeded at reviewed clean HEAD
`b5f589c58cf08b312a743a911505386ab04f0df2`. Check-only and execute each returned
zero. This is target compiler/file evidence; the new image was not uploaded.

## Bound inputs and execution

- Source: `3a08ddeb437c47940a1a6b2ba8e63f7843e5b242ca68ae38c27849bd4e33dbb0`.
- Manifest: `aa350c657fbff328dc139793c4ccd09c86ce45e05bdc7acaa20822498beb7d6e`;
  all128 exact working-file pins remained unchanged after completion.
- Launcher: `70e1f016cec041b40c98c7c5dd5ee20223d75c4a876c76d2fcdea3d790d63827`.
- Board boot: `55c386b9-fe6d-4388-a7f4-1d91e0bb49d8`.
- Fixed static/default profile: MATCH0, MOTORS_ALLOWED0, probe1; empty setup grants.
- One query, one compiler operation and236 transports. All eight closing checks
  passed: local, identity, initialization, builtins, remote sources, installed
  pins, overrides and artifacts. No retry, upload, reset or MCU read occurred.
- UTC start21:21:40.893975 and finish21:27:31.341220 on25September2026.

Exact commands, durations and unmodified outputs are in
`P7_app_motor_observe_compile_raw/native_static01_invocation.json`. Result
`native_static01/result.json` SHA256 is
`24d12778bbb337a5cba411fadab5c5e7a8fd69f99beee7b68ac110c31613622b`;
artifact receipt SHA256 is
`5ceba77dde7c493d66398bfd6d8e0e27e56345612290cb8fef9328f24b87625b`.
The compile owner `app-motor-observe-static01` is consumed.

## Actual artifacts and limits

Eight artifact identities/hashes matched the final observation. Raw ELF is
172648bytes, SHA256
`2fd70da8edc66daa9c54162c028857692d07a1e8c7f960db8384ec7886f30e24`.
Debug ELF is1837380bytes, SHA256
`33e3b34dc11ee5be56b8b94bca168eb0bdff5de3e4721fcf7ac9e8c015047324`.
Packaged flat binary is95360bytes, SHA256
`85b05c564fd3545c6b6e16fb64ed2aef8893226e32048309f1b71f97a5db4b6c`;
its exported copy is identical. No duplicate firmware/debug files were downloaded.

CLI reports95360bytes program storage and170868bytes globals, leaving91276bytes
under its262144-byte accounting limit. Structural package validation reports
91280bytes of RAM tail,208bytes data copy and170632bytes BSS clear. These are
different accounting observations, neither measured live free RAM nor a stack
or WCET qualification. Static package/TLS validation passed; six native TLS
symbols were checked and no weak undefined symbols remained.

The latest flashed firmware remains D190's inhibited four-epoch diagnostic.
D160/D161's original full-application IO fault remains unreproduced and unresolved.
New file ABI and entry observations must establish the changed Report.polls field
and actual symbols before a separately reviewed finite upload/capture. Historical
addresses, old consumed scopes, physical gates and motor-run permissions do not
carry over. Independent actual review is recorded separately in
`../reviews/P7_app_motor_observe_compile_actual_review.md`.
