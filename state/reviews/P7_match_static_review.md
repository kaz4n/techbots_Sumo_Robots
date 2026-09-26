# D241 production static MATCH: source and host review

27 September 2026, Dubai. Separate Codex reviewer with reused project context.
Read-only source/delta, fixture and saved-result inspection; no reviewer test,
native command, source edit or motor operation. This is the sole review edit.

**PASS for the fixed production compile/deploy/identified-delivery tooling.
No open material finding.** The remaining current target compile is distinct
from this host acceptance. No M1 upload or physical qualification is admitted.

## Frozen inputs

Independently rehashed all 47 pins in
`state/analysis/P7_match_static_raw/preparation_manifest01.json`, 8074 bytes,
SHA256 `de4c1c3fd154f79e778b4da867c1eb3ce93a6d24a84fc400bc12786cdd519b23`.
Reconstructed all six forward and reverse projections against the exact retained
D222/D227/D240 source bases; both directions match byte-for-byte. Every function
in the six new tools is under 60 source lines. Existing tools, firmware, config
and locked tests remain unchanged.

| New source | Bytes | SHA256 |
|---|---:|---|
| compile_match_static.py | 17853 | `dc1cb02c5376828da12497d59925a482b4dbba1fa74b8942e3e57d853cd89baf` |
| match_static_policy.py | 6819 | `d81852c4f78b94794698abe2c375ffcb20a28a6d5edd37d9fccc4045e772645c` |
| match_static_compile_remote.py | 5206 | `b248cc75c5142e76b4b26fea043d24bbd84267ace9e9c92ff5f68d4e5dd8da6c` |
| match_static_upload.py | 13689 | `d7f9395ad4b1d491f20dc9976fa8d9eb746c8fc9b5b8d5ef977c3c1a4fd4a8ed` |
| deploy_match_static.py | 28596 | `87b85c1ebc3a80d83c7cf22c71e8b23c314395773ae95538cf90f449fda43149` |
| run_match_identified_delivery.py | 11291 | `60b7b69926defabe2dc364d6c64c5fb58ea1d3f8f7290b86b1c4929bd5169535` |

All paths above are under tools/. The 5000-byte contract is SHA256
`b58651f7f69a3e8e2ccb7f60df75eb217ca7f562563a1fac33a8349ee26554b7`;
4288-byte validation is
`0acb0ffb6abbed599e9256c7cdec38f37d8dc11510407232be9ce5d011228666`;
14819-byte focused test source is
`fdaf7441ab5061dd013ebe55238cdee858b287bd82741776a281bf93e5f1e2e4`.

## Fixed compile and artifact behavior

The only admitted tuple is ordinary app.ino, MATCH=1/MOTORS_ALLOWED=1, all eight
commissioning/probe macros explicitly zero, static linking and Immediate startup:
`arduino:zephyr:unoq:link_mode=static,wait_linux_boot=no`. Other profiles, M0,
boolean motor arguments and escaping attempt names refuse. The historical-source
compiler admission, exact Git/current input closure, exclusive owner, one query,
one jobs=1 compiler, descriptor observations and nine closing checks are reused.

Reviewed saved primary sources identify both installed menu options, the CLI
comma-separated FQBN grammar, static/Immediate packaging recipe substitutions,
and zephyr-sketch-tool's flag ORs 0x02|0x04=0x06. These support the expectation;
actual target properties must still match the exact tuple and controlled recipes.
There is no fallback to another FQBN, boot mode or command.

The private metadata projection changes only FQBN, boot mode and the two exact
post-objcopy package recipes. The artifact projection first hashes the original
validator/TLS sources, then changes only its exact 16-byte package-header flag
expectation from 2 to 6. Full seven-file bounds, three-ELF allocated image and
initialization agreement, inherited TLS tuples, raw flat-body reconstruction,
ELF package, exported package and native descriptor closing checks remain. The
host positive packet passes the real validator; flags0/2/4/7 and damaged bodies
refuse. This is not merely a header or reported-size check.

The saved real constructor records 135 compiler/source inputs and 105 staged
files, source digest
`9337c580d3451de6f2cfe02ebcaa19abf75b147cf7e35bca34defcc562ed1c3e`.
The requested actual command-construction measurement records a 124465-byte
source payload, packed29649/32768, chunks16384+13265. First/second/observation/
closing command sizes are29368/25450/9267/7760 UTF-16 units including maximum
identity fields, below30000. Transport was replaced by an argument recorder;
no command executed. command_geometry01.json is1144 bytes, SHA256
`c16db4b3903b2f42b496d8563f48778633fe09730e07076a0056fd68f01cbad1`.

## Deployment and identified-delivery boundary

The precompiled route checks the complete D241 build/artifact records, current
source/config against historical Git blobs, installed runtime/target bindings
and the fixed static/Immediate upload argv. It does not compile or retry during
upload. Production qualification and human authorization reuse the exact existing
match_deploy methods in a private module with the selected FQBN. Qualification
binds source/raw/package/target/runtime and stand or ring operation; authorization
binds the full current request, corresponding STAND OK/RING OK and bounded UTC
validity. No new GATE P4 or other phase-gate field is invented. Fixture authority
documents are synthetic and supply no actual permission.

Standalone deployment retains the nondefault-session refusal. The paired route
requires the exact compiled positive uint64/session-prefix identity, stream1,
four native-dump grants and the same production qualification/authority. It
consumes one prefix owner, binds the claim, arms the fixed identified receiver
before one upload, and keeps the accepted D240 generic complete-envelope/session/
CRC/CSV validator and first/secondary-error closure. Its source differs from D240
only in deployer and schema identities; no new wire repair, reset freshness,
router operation or runtime control path is introduced.

## Focused evidence and limitations

host03 records six Windows methods PASS, no failures/errors/skips,22.218 seconds
unittest and22.626 seconds outer execution, with all eight execution inputs
unchanged. Real temporary Git/compile/qualification fixtures admit a valid
production baseline before negative cases. Coverage includes current compiler
construction, metadata, complete synthetic artifacts, checked remote bundle,
decoded upload payload/argv, both production stand/ring authorities, wrong
authority/image/boot metadata, paired receiver composition, session collision,
changed claim, one controlled five-operation upload closure and consumed-owner
refusal. No physical observation is represented by these fixtures.

The Windows remote-bundle fixture uses an empty pwd module solely to load the
unchanged Linux-only helper definitions. No pwd function or native descriptor
operation is exercised; this does not claim Windows execution of that helper.
host01's historical-HEAD guard refusal and host02's missing-pwd failure, including
their exact earlier fixtures/contracts, are preserved. Corrections affect only
the fixture's current compiler owner and disclosed import seam. No production
guard was relaxed, and no broad inherited suite was repeated.

A clean exact committed checkpoint may proceed to the separately authorized
single compile-only check/execute tuple under D241. Its actual source/metadata,
native ELF/TLS/package and closure result still require reconciliation. This
review supplies no M1 upload, STAND/RING permission, initialized ordinary-app
timing/RAM measurement, physical sensor evidence or human phase acceptance.
