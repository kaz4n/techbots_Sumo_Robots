# Fixed inhibited B4 upload observation

2026-09-26T21:53:37.942995+04:00. At clean commit310f96066a0fb95c66d948e3128cd67c49c5f344, the admitted D221 driver completed check-only in2.208s and one upload sequence in29.392s. Nine transports returned0. The returned compact upload report records one UPLOADED attempt and a reaped, non-timeout child returning0; measured child interval is12.001s. All first/postcheck, local, prerequisite, transport and finish error lists are empty.

Root closuref7b5967d verifies230 current/native-HEAD inputs,195 unchanged host inputs and161 runtime input hashes including the ADB executable. Result6d5e7b10 and driver3dfd8484 preserve the records. The complete1793-byte durable upload result87bc88a9 remains on the board and was not retrieved; this observation accepts the returned compact completion only. Independent actual reviewca817e15 is FINAL PASS for this returned upload completion.

This is fixed B4/static/default/MATCH0/MOTORS0/otherprofiles0 source9044ebbb, raw82896B6fcad2f0/package82912B84667b0a. Upload is not MCU readback, initialized runtime, physical inhibition or qualification. D219 capture independently compares complete loader/sketch flash before SRAM. User reports board only; all grants stay absent.

The run recreated /tmp/remoteocd. Its current inode/content inventory has not been observed, so consumed D220cleanup must not be reused. Retain that fresh scratch pending separate verification, plus checked build artifacts, source and unique upload evidence.
