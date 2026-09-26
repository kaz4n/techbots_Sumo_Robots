# D208 ordinary application static compile: independent actual review

Date: 2026-09-26. Reviewer: `const_cleanup_review`, review only.
Disposition: **FINAL PASS for this single compile-only attempt.** No open
material finding. Attempt `ordinary-app-static01` is consumed; this acceptance
does not admit another compiler invocation or a firmware operation.

## Scope and method

I reviewed the adopted D208 contract, previously accepted independent source,
host and admission reviews, actual outer invocations, all 230 saved transport
intent/result/stream groups, query/compiler responses, complete artifact
observations and local closure. I used local byte/hash comparisons, strict JSON
parsing, AST/literal data extraction, bounded payload decompression and read-only
Git blob inspection. I did not import or execute a project subject or test,
invoke ADB or a compiler, retrieve additional board files, or run firmware.
Only this new review is written by this reviewer.

The native reviewed commit is
`9bdd38aeb312404bc1cd2a3b3fa7e7f621f3bad5`. The accepted actual admission review is
`P7_ordinary_app_static_compile_admission_review.md`, 14075 bytes,
SHA-256 `7bf556e366d9e0cc21f4a6f3da10e6edc4aa4ca2dd0353ce8c3f3e8affc5ef41`.
It remains the independent admission decision, including fresh owner/resource
checks and the precommit evidence-preservation corrections. I also compared
the current inputs with their exact committed blob bytes, rather than assuming
Git text normalization preserved evidence.

This review accepts target Linux compilation and the resulting checked static
artifact packet. Artifact bodies remain on the board; I independently reviewed
the recorded execution of the exact pinned validators and their complete
repeated reports. I do not claim a separate local ELF parse or a new board
measurement. The mutable root validation document is not an input pin for this
review; its observed-result section was checked for consistency.

## Evidence identities

Paths in this table are relative to
`state/analysis/P7_ordinary_app_static_compile_raw/`.

| File | Bytes | SHA-256 |
|---|---:|---|
| `native_invocations01.json` | 4533 | `469f2d38b718dcd0fc8c7f76dcac34258dc2dffe8fbe5ebc931a9282e13e4181` |
| `native_scope01.json` | 6216 | `6a17b23a9d6d68cd75e65c846aaeebf9868d3c30865e3e5d029c9fa1f5f1a5e1` |
| `manifest_preparation01.json` | 15551 | `7dcc86b56e7326e4bc6c0eb86d2bf128ae08eb1a70bfc91a130ecf03412de4f1` |
| `native_static01/intent.json` | 820 | `9f0b1e7c86985906e363a48ce3f37401ff4e14838d360102f0974eaab441b17f` |
| `native_static01/result.json` | 1565 | `221d02be2de722a8886a142328d3accb147cf1ab89b60ed9857e62fdd303aeb0` |
| `native_static01/artifacts.json` | 9281 | `275ebb61be4a0487fe381d915ec28eea4634926b1d06a627850266f5c0a750e0` |
| `native_local_closing01.json` | 4221 | `21917a13f6e536eece5a82ecb84c83ebf960323aa303fa5d032226dbf76a981d` |
| `host_closing01.json` | 86354 | `cd0c8ff33ca7a4456e883bb7f7e4a1a4f0a9cff3bcb6def820bb2ff7ab1f544f` |

The actual manifest is the accepted 12940-byte document with SHA-256
`a5e8f8b4b78312245c7cde3e86a39db9073b5ef9e5fa2806a3d39eece8600bb7`.
The sealed source/host review remains 19198 bytes,
`e69387e0aa28f993972c4eaf6bf8ffcd236a70fb076cf59f638afc1c94d4a78c`.

## Source, manifest and clean-commit provenance

Independently compared all 191 coordinator pins, 125 manifest pins and fifteen
scope pins. Their union contains 200 distinct file paths; every current byte
length/hash and every committed blob at the reviewed HEAD agrees. Thus the
committed subjects, independent oracles, contract, supporting code, source,
manifest and admission material retain the reviewed bytes.

The exact current source inventory contains 105 files. Independent ordinary
source mapping produces 104 staged files totaling 764405 bytes; only the
unmapped placeholder is excluded. The staged paths, file bytes, hash map and
four directory paths agree with `manifest_preparation01.json`, the saved stage
inventory and the actual local stage. Source and stage entries are ordinary
files/directories without reparse points or multiply linked files. Reserved
sketch-local names, case collisions and sketch overrides remain rejected by
the accepted ordinary mapper.

Reconstructing the digest from the mapped destination names, NUL separators
and file bytes in the defined `Path` ordering gives
`9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a`.
It agrees with manifest, intent, scope and result. The canonical board source
is `/home/arduino/sumox26_codex_build/` plus this digest plus `/app`;
the separate build owner is
`/home/arduino/sumox26_codex_build/ordinary-app-static01`.

The scope has exactly the fifteen accepted roles. It retains ordinary
`app.ino`, default/wait startup, static linking, `MATCH=0`, `MOTORS_ALLOWED=0`,
the default zero diagnostic-probe selection and all seventeen ungranted
hardware/software acceptance switches. No production source or safety setting
was changed for this compile. The diagnostic source mapping and diagnostic
entry are not substituted for the ordinary application.

## Actual operation and closure

The saved outer check-only invocation returned 0 in 0.622214 seconds. The one
execute invocation returned 0 in 414.060572 seconds, with empty outer stderr.
Both name the reviewed HEAD and fixed launcher; execute uses its dedicated
bytecode destination. Outer stdout parses to the saved native result. The
intent/source/manifest/scope bindings agree, and the result is
`COMPILE_CHECKED` with `first_error: null`, one query, one compiler and 230
transports. Native timing runs from 11:41:13 to 11:48:05 UTC on this date.

I reconciled every consecutively numbered transport, its exact intent/result
argv and timeout, returned status and streams. All 230 return 0 with empty
transport stderr. Windows command lengths, including the terminating NUL,
match the receipts; the maximum is 29605 UTF-16 units, below the 30000 bound.
The exact categories are 107 identity checks, 104 pushes, nine checked commands,
two initialization inventories, two builtin inventories, two source-set
observations, one command-owner creation, one source admission, and two
artifact observations. No upload, reset, debug-server or MCU-memory operation
appears in this dispatched sequence.

All identity observations retain serial `2629958581`, Arduino UID 1000, the
reviewed CLI hash and boot `55c386b9-fe6d-4388-a7f4-1d91e0bb49d8`, with empty
conflicts. Observed board home free space stays between 13892399104 and
13913214976 bytes, above 1 GiB. Source admission reports `reused: false`;
all 104 push destinations and local source hashes agree with the exact staged
set. Both remote source-set observations equal that complete hash map.

Both complete CLI initialization observations and both builtin observations
match their respective pinned historical baseline projections, with the
current boot substituted as specified. That projection ignores only
`mtime_ns`/`ctime_ns` and canonicalizes lists of objects; it does not discard
file hashes, permissions, owners, identity or inventory membership. The three
initialization files and five builtin files are preserved. Both installed
policy checks contain exactly the eighteen expected paths/hashes in the
specified order. Both override checks return empty output without error.

All nine checked children report `COMPLETED`, return 0, `timed_out: false` and
`reaped: true`. Their packet/child argv, clean environment, deadlines and
five-second reap allowance agree. Base64 streams are canonical and decode to
the exact saved child streams and declared lengths. No retry is present.

The eight closing checks are all `PASS` with null errors: local, identity,
initialization, builtins, remote_sources, installed_pins, overrides and
artifacts. The root local closure agrees with the independently counted 972
native files totaling 1650045 bytes and unchanged input/source maps. Its local
free-space observation is 7405113344 bytes. This is a checked closure receipt,
not a continuing reservation of resources after the attempt.

## Query and compiler acceptance

The actual checked command at `0221-checked-command` is the expanded-properties
query; `0222-checked-command` is the compiler. Both use the fixed absolute CLI,
`--config-file /dev/null`, FQBN
`arduino:zephyr:unoq:link_mode=static`, exact build/output/source paths,
`--jobs 1`, C/C++ flags `-DMATCH=0 -DMOTORS_ALLOWED=0`, and explicit library
discovery phase zero. The query adds only `--show-properties=expanded`.
The query takes 1.605218 seconds under its 60-second deadline; the compiler
takes 226.068115 seconds under its 720-second deadline. Both are reaped and
have empty child stderr. These are compiler timings, not MCU execution timing.

Independently parsed the raw child JSON, rather than only the caller's
acceptance summary. Each response has 318 unique build properties, successful
status, no error/upload result and the expected board/build platform
`arduino:zephyr` version `1.0.0`. All 84 controlled command-property keys and
their exact values match the pinned static reference after only the defined
build/data path substitutions. All seventeen metadata expectations match,
including project `app.ino`, core/variant, default/wait boot, static link,
compiler paths, safety flags, empty extra flags and package extension. The
external-library field is absent and therefore the accepted empty default;
there is no claimed library-discovery result beyond that exact policy.

The saved `compile/*.stdout.json` objects equal the raw child JSON objects.
Their text-file newline representation is not confused with raw child stream
bytes. The actual CLI version and resolved data/user-directory commands are
the fixed accepted preflight commands; the installed hashes and override
checks bracket the compile. Query success alone is not used as build evidence.

## Artifact provenance and complete report

The initial and final artifact programs are byte-identical. Independent AST
extraction and bounded decompression of their payload gives 72069 bytes,
SHA-256 `423a29bc44fb2f6f7b9a34003f14e0da41431d6d25e05a4df4debfc7cad7978e`.
The embedded sources equal the exact reviewed projections/support bytes:

| Component | Bytes | SHA-256 |
|---|---:|---|
| D208 remote projection | 6845 | `71c189ea3c354b7ccb969b35ae3f1a92a517380735059d00ff4c735b45cf4389` |
| D208 adapter projection | 8219 | `d1a78ad713d0550ed52805a6751640823a31ce4e96edafc3c058a7587c5e4863` |
| File observation helper | 33321 | `8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8` |
| Native TLS validator | 3718 | `cd52a29a32b8ae1da4bea51dd55d9011386dd4be0ca537195bb124d13031d6c0` |
| Base artifact validator | 18322 | `d30372dd4b8fb8c2661d00affc4a215cc88e3f62511995ff6303827bed4b7368` |

Projection bytes were independently reconstructed by the exact counted literal
substitutions from the pinned originals. No validator body was run by this
reviewer. The actual payload retains the full descriptor, regular-file,
identity, content, package, loader/TLS and closure validators previously
reviewed and exercised by the independent host suites.

Both complete observed artifact objects equal `artifacts.json`, including all
eight build/export file hashes, sizes, paths and saved file identities, loader,
TLS source, layout and postchecks. The schema is
`ordinary-app-static-artifacts-v1`, status `ARTIFACTS_CHECKED`, with no first
error. The ordinary layout result is
`STATIC_ORDINARY_APP_LAYOUT_PACKAGE_PASS`, and its nested validator is
`STATIC_NATIVE_TLS_LAYOUT_PACKAGE_PASS`. All seven aliases are exact identity
mappings and their reported hashes equal the corresponding build-file hashes.

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `app.ino.bin` | 92928 | `6f5f531b114219d712d857b4ac89ad161ceb217211207788a27443b7d4ab6db7` |
| `app.ino.bin-zsk.bin` and identical export | 92944 each | `7fa9d41da043931e1237712e1e88bda4151c82933af2ecec97ce3a02184d23ad` |
| `app.ino.elf` | 170376 | `aaeeb64025dae2b2f8bf0458a39c110377ca8d5e4c9f833fae75444a181f6db5` |
| `app.ino.elf-zsk.bin` | 170376 | `1bba8a9b8f2bc91a7d28d017602606e0644b28bb360f2ed87018dc18e5b4d609` |
| `app.ino.map` | 431425 | `dc6f91c98f23418704c005bd847ccf604544d8f12697ce856337219bfb8627b8` |
| `app.ino_debug.elf` and `app.ino_temp.elf` | 1751548 each | `71e512382e764810ed02eec110e3c1c003244d41d608b145ea400e1e8235ab90` |

The loader and native TLS source hashes are respectively
`39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd`
and `68bb147615813666d528b9bd650e02fb8e240f0db841939e8460d7a52fd2ee70`.
The report preserves all six native TLS symbol results and no weak undefined
symbols. Loader, TLS-source and complete file postchecks each pass with null
errors. Export/package equality and debug/temp equality are exact byte-hash
claims from these validated observations, not inferred from filenames.

The checked layout reports entry 135266321, 208 copied data bytes, flash range
135266320 to 135359248 and 693488 bytes remaining. Its zeroing span is
536951136 to 537118408, or 167272 bytes; the complete `.bss` section is 167584
bytes. Those quantities must not be substituted for one another. The
structural RAM range is 536950928 to 537118720, leaving 94352 bytes under the
validator's bound. The separate CLI summary gives 167796 global-allocation
bytes and 94348 bytes remaining. Both static accounting reports are retained
without inventing a runtime interpretation or an explanation for their
four-byte difference. Neither is measured live free RAM or stack headroom.

## Preserved limitations and final acceptance

The accepted host evidence remains Linux 80 caller plus 55 remote passes,
Windows 77 caller plus 34 remote passes and 24 explicit skips with matching
Linux passes. The original 78-pass/two-failure fixture run, pre-execution
fixture findings and exact subsequent fixture corrections remain preserved.
This native success does not erase those records or convert skipped Windows
cases into Windows executions. No subject was changed to obtain acceptance.

No firmware was uploaded, reset or read through MCU memory in D208; this
compile therefore leaves the previously accepted D207 flashed image unchanged
by this operation. It does not establish ordinary package loading, ordinary
runtime behavior, full initialization with granted peripherals, sensor
acceptance, live memory use, stack high-water, timing/WCET, powered motion,
MATCH/B4 acceptance, a phase gate or motor-run authorization. Ordinary static
addresses and entry behavior require their own artifact inspection before any
later finite runtime observation; diagnostic capture layouts cannot be reused
by assumption.

The exact single ordinary static/M0 compile and checked artifact packet are
accepted. The next bounded work may be separately prepared file-only ABI/entry
inspection; no next device action is admitted by this review. This review is
sealed after final byte/hash reporting. Reviewer writes stop here.
