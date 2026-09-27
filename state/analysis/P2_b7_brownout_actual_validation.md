# D244 current UNO Q compilation

27 September 2026, Dubai. **All three compile-only operations passed.**
The B7 M0 and M1 variants pass complete package/layout checks. The ordinary
competition package and final ELF are byte-identical to accepted D241/D243.
No upload, reset, MCU operation or motor run occurred.

Frozen build HEAD: `97e32fded4f36bdb759fd273965ee8ce72301753`.
Common application source SHA256:
`85b320de79f0fe26602bd6b714d77136718f4a6ab32ba989ea8322b7b92a481a`.
Source/host acceptance and preserved oracle failures are in
[the host validation](P2_b7_brownout_validation.md). The independent native
review is [P2_b7_brownout_actual_review.md](../reviews/P2_b7_brownout_actual_review.md).

| Build | Elapsed | Transports | Package bytes | Structural RAM remaining |
|---|---:|---:|---:|---:|
| B7 M0, static/default startup | 433.208 s | 243 | 84,284 | 90,256 |
| B7 M1, static/default startup | 265.829 s | 25 | 84,656 | 90,256 |
| MATCH M1, static/Immediate | 265.126 s | 25 | 92,092 | 91,280 |

Every operation used one compiler process, one properties query, nine reaped
checked children and nine successful closing checks. The B7 input manifests
bind143 files; production binds139. Every stage maps109 files. The147-path
sparse checkout union is a separate count. The two later builds reused the
verified common remote source directory; they each performed a new compilation.
Pinned board boot `55c386b9-fe6d-4388-a7f4-1d91e0bb49d8`, compiler/tool identities,
source sets and artifact observations matched their opening and closing checks.

## Exact retained artifacts

- B7 M0 owner: `P2_b7_build_raw/commission-b7_brownout-m0-4adb205ea983`.
  Package SHA256
  `e370976cc89cf36dd70226c48813cddf3d53d298d4db9831b7b4ba7449cced0d`;
  final ELF153304B SHA256
  `2c30e55a3b128a32edfb11162d50d6ec954ea2b4ad4b394621977fc4243a7cd0`.
  Durable commit3baf77b5 retains1025 original files/1780354B.
- B7 M1 owner: `P2_b7_build_raw/commission-b7_brownout-m1-4adb205ea983`.
  Package SHA256
  `b7e2f20b8e286d5baf9488f3b8350886e6f6162ca13ee508de76a861b0191ae9`;
  final ELF157432B SHA256
  `ac0c1a21c3e17fb38a8de188d56f08c7c246783b734b95a9dd976e980a02d925`.
  Durable commit3aca4532 retains153 original files/1041368B.
- Production owner: `P7_match_static_raw/match-static-match-m1-9fceb7202abf`.
  Package SHA256
  `7895a4d8991bd2158e63c69cb37ebcdc4f39632311a1dbf47401c3a34f664c86`;
  final ELF165836B SHA256
  `ba9766a8a207564fa0d2bd25dd6472a16f176f09740eda4689e167e81536a666`.
  Both equal D241/D243 exactly. Debug/map artifacts are separately bound.
  Durable commit990a4749 retains153 original files/1039256B.

The three `P2_b7_build_raw/native_*_01` folders retain original outer command,
stdout/stderr/exit/time receipts and byte-for-byte copy manifests. All1331 copied
owner files total3860978B. No transport stream was normalized. Checked remote
artifacts and source identities remain retained for provenance/reproduction.

## Practical boundary

Both B7 builds use the real application and exact dedicated flags; all competing
bench macros and MATCH are zero. Production uses MATCH1/M1, the existing eight
probe flags zero, and B7's verified default zero. Byte-identical production output
establishes isolation of the new bench feature in this compiled image.

Structural RAM is linker accounting, not measured free RAM, stack or WCET. CLI
memory summaries are four bytes lower and are not substituted for these figures.
All current setup grants remain absent. The M1 artifact is compile-checked, not
an operationally qualified motor image. D245 supplies a separately reviewed,
host-tested stand-only deployment route, with no actual deployment performed.
See [deployment validation](P2_b7_deploy_validation.md).

Physical B7 remains unaccepted: half-charge, assembled wiring, motor direction,
twenty actual full-power forward/reverse cycles and independent uninterrupted
uptime are not measured. Fresh specific STAND OK, source/setup qualification and
human phase gates remain required. Board-only evidence cannot close them.
