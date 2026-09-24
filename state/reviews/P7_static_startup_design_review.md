# D153 passive startup collector design review

25 September 2026, Asia/Dubai. Separate fresh-context same-model review of the
contract and retained evidence only. No implementation body was available or
executed; no board command, upload, reset, MCU read or compiler ran in this review.

## Findings

No open BLOCKER, MAJOR or MINOR finding in the reviewed scope.

Reviewed [contract](../analysis/P7_static_capture_remote_contract.md) SHA256
`0b2cb941060954ea863f03194d10b7e3decf274bc3891d6055a6b2324b8e48fb`
and [bindings](../analysis/P7_static_startup_raw/capture_bindings.json) SHA256
`c2c87df6165556602a5a79472caedf0755c070b2e2f3e0b834f17ab0de5c0d32`.
Before this disposition, the coordinator clarified malformed decoder-return
rejection, the collection deadline versus bounded reap/unknown completion,
descriptor-based creation and directory drift checks, and consumption after
mkdir even if claim persistence fails. These are now explicit contract terms.

Independent local comparisons found all five bindings consistent with retained
receipts: OpenOCD/config/swj match `upload_inventory.json`; loader ELF
2303728 bytes/SHA39d4a4fd and flat sketch93096 bytes/SHA5f08afe0 match
`P7_static_link_probe_raw/native_actual/result.json`. The boot and UID also match
that retained packet. This verifies the bindings' provenance, not their future
installed state. Collection must perform the stated fresh checks.

The contract correctly adopts the corrected ELF-derived loader reference,
263680 bytes/SHAe9322826, preserving the earlier BIN mismatch finding. Current
unchanged helper, pure decoder and loader utility hashes are respectively
8ba9b190, b7ab979d and885c4e42. Reusing their checked filesystem/parser operations
avoids another framework and does not reuse a consumed native grant.

The finite18-read plan requests713656 bytes. Both complete before-flash images
must match before RAM sampling; incomplete captures never reach interpretation.
Attempt ownership, exclusive records, per-process bounds, process-group timeout,
independent seven postchecks and preservation of the first failure provide an
adequate specification for focused host tests. A completed capture may still
report a fault, no progress or after-flash mismatch. The sampled process and
directory checks make no kernel-wide exclusivity claim.

## Verdict

PASS for implementing and independently host-testing the D153 passive collector
only. Test expectations must freeze before implementation execution, followed by
separate code/receipt review. This is not approval of a native invocation.

The later host composition must separately bind reviewed source/HEAD, the D144
packet and a known clean new upload outcome, then durably consume a fresh capture
claim before launch. No upload implementation, production static admission,
current MCU state, live memory/stack/WCET, physical acceptance or human gate is
established here.

## Follow-on upload configuration finding

Source inspection supports `--config-file /dev/null` with an explicitly
constructed child environment containing the fixed
`ARDUINO_DIRECTORIES_DATA=/home/arduino/.arduino15` and
`ARDUINO_DIRECTORIES_USER=/home/arduino/Arduino`. At pinned CLI commit
01f3d4f2ba7c2eaafb5dc710c8a1903af7762fea, explicit config selection precedes
environment/default discovery, the file is read directly, and environment
settings are injected after YAML parsing. The retained source audit under
`P2_app_override_raw/source_audit/primary` provides the same source and identity
receipts. [CLI main](https://github.com/arduino/arduino-cli/blob/01f3d4f2ba7c2eaafb5dc710c8a1903af7762fea/main.go#L43-L58),
[selection](https://github.com/arduino/arduino-cli/blob/01f3d4f2ba7c2eaafb5dc710c8a1903af7762fea/internal/cli/configuration/configuration.go#L121-L150),
[environment injection](https://github.com/arduino/arduino-cli/blob/01f3d4f2ba7c2eaafb5dc710c8a1903af7762fea/commands/service_settings.go#L189-L213).

The pinned go-paths-helper1.14.0 delegates reading to `os.ReadFile`; YAML3.0.1
accepts an empty input without changing settings. Thus the empty-config route
is supported by source; it has not been executed here. A future contract should
check `/dev/null` as its expected nonsymlink character device and discard ambient
configuration variables by constructing the child environment from literals.
No new empty config file is necessary. [File read](https://github.com/arduino/go-paths-helper/blob/v1.14.0/paths.go#L399-L401),
[empty YAML](https://github.com/go-yaml/yaml/blob/v3.0.1/yaml.go#L148-L163),
[empty stream](https://github.com/go-yaml/yaml/blob/v3.0.1/decode.go#L139-L153).

Only this small review file was added. Local comparisons stayed in memory;
there was no generated binary, duplicate source tree, cache or disposable output.
