# D145 diagnostic collection result review

25 September 2026, Asia/Dubai. Separate fresh-context same-model, read-only
evidence review. Only this review was written; no board command, implementation
execution, build, temporary copy or bytecode was created by the reviewer.

**PASS for diagnostic byte collection and identification of the rejected
encoding. New BLOCKER: none. MAJOR: none. MINOR: none.** This is not a phase gate
or static artifact admission. The existing rejection remains at
`state/analysis/P7_static_link_probe_raw/static_artifacts.py:268` under the frozen
type allowlist in `state/analysis/P7_static_artifact_contract.md:146`.

## Independently checked evidence

- D145 authorizes one checked read, preserving D144's consumed compile authority.
  The exact reviewed plan remains SHA256
  `5f52f30631fe07d5ecaa0105e46f1b08293421f2d9ae4e10380232e72fed8de9`.
  Its prior review closes the transport/path admission and removable-assert
  findings. Current runner983e86d7/helper8ba9b190 and all17 input pins match.
- `diagnosis-v1/0001.json` is the only numbered diagnostic receipt: sequence1,
  phase read, board2629958581, timeout60, exit0, empty stderr, no error. The
  captured argv contains the exact unchanged bootstrap and compressed helper
  bytes, action `read`, original runf0220228320c4b2aa20c3e5e8264c813, offset0,
  length170616 and the original ELF hash. There is no query, compile, upload,
  reset, retry or remote mutation action in this receipt/composition.
- Decoding the captured canonical base64 independently produces the exact local
  ELF170616 bytes, SHA256
  `5cc2dfdec597f1421d6250936569bc113542723c362786f23be62834b5ba0386`.
  Full FileRecord, Claim, boot identity and run/build/artifacts directory IDs
  match the pinned historical receipts and result. The helper read path checks
  current boot/directory identities and stable file observations before returning.
- `result.json` records DIAGNOSTIC_ELF_COLLECTED, one read, zero query/compile
  attempts and no postcheck errors. Independently rehashed all17 inputs,103
  current source files and102 staged files; source digestfcddbd8e remains exact.
  This corroborates the reported local postchecks without another board read.
- All25 original D144 command receipts match their retained hash index. Original
  result SHA256bc527182 remains FAILED/layout; compile0 and unsupported-symbol
  rejection are preserved. The frozen D142 validator, contract and public/private
  oracle inputs match their original hashes. Git comparison with1e35b70e shows
  no change to those paths, the old run, production, tools or existing tests.

## Actual ELF diagnosis

Independent in-memory ELF32 parsing reproduced all2242 symbols, the complete
encoding histogram and all six rejected records in `symbols.json`. A fresh
local GNU readelf invocation reproduced retained `readelf.txt` exactly. All six
are GLOBAL/type6/default visibility/ABS/size0:

| Index | Name | Value |
|---:|---|---:|
|1557|`_TLS_MODULE_BASE_`|0x8|
|1598|`errno`|0x14|
|1615|`_localtime_buf`|0x1c|
|1872|`_strtok_last`|0x18|
|1927|`z_tls_current`|0x10|
|2071|`_rand_next`|0x8|

Readelf labels type6 as TLS. These records violate the unchanged type0-4 rule;
this explains the observed rejection without admitting them. The final ELF has
no PT_TLS program header, SHF_TLS section or relocation section. That does not
prove absence of resolved TLS accesses, correct native thread ABI or runtime fit.

Reviewed root report `P7_static_elf_diagnosis_validation.md` at SHA256
`a9db7c82deea642825ceea82736b35ca6b38490b2da0e78089fbdc13ba98307a` agrees with
these observations. Primary-source provenance and native use analysis are
separate work, not established by this review.

Receipt SHA256 `de5397d5dbdf21b17cd5a988bf012c9d1c7eef65fb1bfa5a1f8cf869bd79453a`;
result SHA256 `c948e04b2e0a2723f25bb535b30a5d35ee09aae3feee16323b4080eaddbd8581`.
Preserve D144's negative result and this original ELF. Any admission amendment
needs separate scope/review/tests. No further read, rebuild, structural/native
acceptance, upload/reset, motor permission, physical evidence or human gate follows.
