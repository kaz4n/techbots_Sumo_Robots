# D117 initial offline app audit harness dispositions

The first informational inspection reused recorder's `commands` field when the
app collector stores separate `sizes`, `sections`, `relocations`, etc. It printed
the three correct model totals then raised KeyError; retained in tool transcript.
No artifact/product change or claimed target PASS resulted.

`target_5e301997_bench-default_run1.txt` retains the strict unsupported-relocation
assertion: the app has an existing IMU R_ARM_THM_JUMP24 (type30) at0xdf8c, which
the smaller recorder did not have. Readelf's exact collected line confirms its
name/type. The harness now retains those instruction bytes and relocation
identities exactly alongside THM_CALL/MOVW/MOVT; only ABS32 words normalize.

`target_5e301997_bench-default_run2.txt` retains KeyError init_array: app collector
provides supplementary init_array/nm_all command receipts only for the final ELF,
while all three artifacts have full section/relocation bytes. The harness now
requires those exact fields according to collector output and independently
decodes init/fini/startup in all three original ELF byte images.

Run3 completed every identity/byte/startup/import/native-layout/ABI check and
reported the genuine first-default target-fit BLOCKER. Neither harness correction
changes the imported allocation model, capacity, allocation order or product.

`target_ce5a1f4e_bench-default_checked_run1.txt` retains an incorrect expected
section-size assertion: moving the native object to data leaves a164176-byte
Runner plus4-byte UART-owner pointer, giving actual BSS164180. ELF section
alignment8 does not require sh_size itself to round to164184. Run2 binds both
actual symbols and uses the unchanged allocator rounding separately. No target
bytes, source or heap-model rule changed; all recorder checks then completed.
