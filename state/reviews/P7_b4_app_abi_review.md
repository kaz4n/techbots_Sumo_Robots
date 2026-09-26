# D215 B4 file-only ABI source and host review

FINAL PASS, 2026-09-26. No material finding remains. This is an independent
reviewer using the same model and reused project context, not a human or
cross-model review. Implementation and oracle authors were separate; their
seals preceded this review. I performed source/AST/byte and saved-evidence
inspection only, without importing or executing the subject, running tests,
or contacting the board. Root performed the first focused host runs.

## Checked identities

Paths below are relative to state/analysis/P7_b4_app_compile_raw unless stated.

| Evidence | Bytes | SHA256 |
|---|---:|---|
| ../P7_b4_app_abi_contract.md | 8820 | f1f1469c2967a198446d5e7fb01bb7388cee6450732b9e9dde1a9b244633224e |
| abi_plan01.json | 33706 | 874da0a9af0477d3ec94cbbc8f86edc03c68229fa0dc7b0c1bc2c7c7dcdf1037 |
| inspect_static_abi.py | 32744 | 4b31dfed3508ebd612abd7de31c5d25e5983c57b802fc55946d3996cf259943d |
| abi_derivation01.json | 33182 | 6f4b7fd790d015b49fb7f25440149f6d10c91402a6487add1c4460f328d99cc2 |
| tests/tooling/test_b4_app_abi.py (repository relative) | 28287 | 82e09db623e9a7f7b4be5fff8784dc4bb1d936f20dd1b55ed2c8261818f88a46 |
| abi_oracle01.json | 6329 | 9f13ad73b24c9d728539ef417ad73fe099ab6e10376debbe68dcdefd530c3976 |
| abi_coordinator_freeze01.json | 23585 | 891e16c301660372ed70ea775939e7f6965285d09fdc4d56d0739ffa78c61a69 |
| abi_host_closing01.json | 5817 | 35323fb4380d9523f3f37d217fe7e7402e3155d3aaec66b574589ee61d02fa13 |

## Source and fixture conclusion

The fixed current D214 M0/B4 manifest, compiler, accepted result and artifact
packet are bound through the real compiler admission and full layout/artifact
validators. Old ordinary artifacts, M1, bool and string metadata are refused.
The checked private projection reconstructs all nine counted metadata steps
and two TYPES/WINDOWS spans, including every intermediate hash. Its resulting
13204 bytes hash to 069af034c960acc478b11ec8c516da58121a8adf2d936531309d298d7ca3feba;
reversing the bounded changes restores the accepted D209 projection.
Seven bootstrap/CLI bodies and twelve reused parser/loader bodies have exact
AST-source identities. StaticAbi.local is exact; its other lifecycle changes
are the declared metadata substitutions. No inherited guard was weakened.

The query retains the exact 185-expression prefix and appends only the
128 specified expressions: 313 expressions, 156 ordered markers, 21 layouts,
seven disjoint Runtime windows, two nested stand fields, eleven member sizes
and 73 enum values. Four fixed file children retain the guarded GDB builder.
New summary helpers require a unique direct numeric RobotResult container,
matching close/name, observed parent size/alignment/containment, and disjoint
contained stand fields. Exact array/wire/index/enum widths, capacity arithmetic
and containing-type sums are checked against fresh answers. Four-byte indices
are an explicit supported-ABI requirement, not a prior target observation.
Layouts remain available for later complete member-offset transcription.

The twenty independent focused methods cover every added marker and numeric
answer with real mutations, each added layout and size/alignment bound,
relocation, nested-container and overlap failures, all new enum values,
array/index widths, pure summary nonmutation, passive import and real current
artifact admission. Historical test classes are not collected. The decision
to retain prior lifecycle coverage by exact body identity, rather than repeat
the full inherited suite, is explicit and bounded; it is not a new full
transport/descriptor campaign. Synthetic answers do not establish target ABI.

No disposable local compile staging path is needed: StaticAbi reads pinned
repository inputs and computes source mapping in memory; it never calls the
compiler's stage, build or source-transport operations. Required local source,
receipts and historical dependencies, and remote compiled artifacts/tools,
remain necessary. This review does not itself perform or expand cleanup.

The host driver is the exact three-step D209 derivative (3491 bytes,
d6113e10dbd69f6909d8dae81fcb56102f6a27c7b0878874417bfd82ac5f749e):
serial isolated/-B runs, exclusive owners, 360-second bounds and saved raw
streams with input closure. The prospective native driver is the exact
seven-step accepted D214 derivative (5151 bytes,
286f710a1b20f611c1134aac339f375d041171426ac3f1508637791e2bda0832),
retaining independent closing checks, earliest-error handling and failed-check
suppression of execute; only the fixed paths/schema and 500-second execute
outer bound change. Native admission remains separate.

## Actual focused host evidence

Both first runs returned zero: Linux 20/20 in 15.679 seconds inner and
28.2744535 outer; Windows 20/20 in 3.106 seconds inner and 3.3798207 outer.
No skips, failures, errors, timeout or retry. I independently reconciled all
40 ordered method outcomes, eight intent/result/stream identities, all
153 current frozen inputs, both unchanged-freeze records and actual empty
Windows TEMP. Stderr identities are Linux
5049ca8065e64dcfea04a958ba06d4b8f997d10f1bf0903889233e6fcc79cbc4
and Windows
3ed242fa4c74b3e4d3751ca17ebf928d2de53ca97f98e2f5c4d2b8632c235d7e;
both stdout streams are empty. Linux fixture cleanup is not claimed as a
separate independent remnant inventory.

Data-only reviewer extraction initially used newline-inclusive function spans
and assumed common replacement tuple shapes; the corrected AST/source and
literal-specific reconstruction passed. These local audit refusals wrote no
subject or fixture and ran no subject/test. The recorded implementation and
driver construction refusals likewise did not change the accepted requirements.

Source/host acceptance permits preparation of the separately reviewed fixed
file-only native scope. At use it must retain clean reviewed committed HEAD,
fresh consumed local owner, embedded board identity/remote absence and twelve
file pins, four 60-second children with five-second reap, 1MiB streams,
400-second transport/8MiB reply, 30000 Windows units including NUL, 128MiB local
free minimum, thirteen remote closing checks and independent local closure.
The prospective 6981-unit command is within that bound. No actual B4 ABI,
MCU contents, upload/reset, runtime coherence, recorder completion, timing,
physical acceptance or motor authorization is established here.
