# Static startup: observed upload dependencies

25 September 2026, Asia/Dubai. Three Linux read-only calls completed with exit0
and empty stderr. No compiler, upload, reset, OpenOCD or MCU read ran in these
calls. Only the third invoked a tool: pinned `arduino-cli version --json`.

| Receipt in P7_static_startup_raw | Bytes | SHA256 |
|---|---:|---|
| upload_inventory.json | 20459 | 21d3b8cbc6546e022b0fa4b55130776ffa44b38297cf1a1ee72ede71311a6b0c |
| upload_include_inventory.json | 3573 | 1aa0f85adac022a3e94fd1f7aebf63a52c53f5aaf347cb0000722685797f377f |
| upload_shadow_inventory.json | 1454 | f57ec3167418f265867ff3e717aa1bf8911541cb08897d43b8c0571a77082fcf |

The first receipt hashes eleven installed tool/config/loader files, records
stable file identities and UID/GID1000 on boot6d4aca1b-ac1f-4caf-b1ef-e127ce3956f6.
The include receipt supplies mem_helper.tcl and observes no home-directory
shadow configs or /tmp/remoteocd directory. The third closes both outstanding
shadow checks in [the source audit](P7_static_upload_route.md): neither
/opt/openocd/mem_helper.tcl nor /opt/openocd/target/swj-dp.tcl existed. It also
confirms CLI1.5.1 commit01f3d4f2b with the executable hash unchanged before/after.
These are observations at their recorded times, not future exclusivity claims.

The source-derived upload selector is the existing raw `build/app.ino.bin`;
the pinned static recipe selects its checked `app.ino.bin-zsk.bin` sibling.
This avoids duplicate staging/builds. The exact command remains unexecuted.
Upload intrinsically may replace the loader and sketch and resets the MCU;
a later scope must include those effects, fresh identities and one-shot handling.
The old consumed D118 upload and D144 compile are not reusable permissions.

Retain all three compact original receipts (25486 bytes total), source audit
and this index for review/reproduction. No binary, source snapshot, cache or
disposable temporary output was created. Physical gates remain pending.
