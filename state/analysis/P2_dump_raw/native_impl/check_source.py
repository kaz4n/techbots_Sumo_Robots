from pathlib import Path
import hashlib, json, re, subprocess
root=Path(__file__).resolve().parents[4]
out=Path(__file__).resolve().parent
files=['src/hal/dump_uart_unoq.cpp','src/hal/dump_uart_unoq.h','src/hal/loop_hook.cpp']
manifest={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in files}
packet=bytes([0x93,0x02,0xa9])+b'mon/write'+bytes([0x91,0xd9,64])+b'x'*64
assert len(packet)==79
assert (160000000*256+115200//2)//115200==355556
loop=(root/files[2]).read_text()
assert '#include' not in loop and 'extern "C"' not in loop
(out/'author_static_checks.json').write_text(json.dumps({'checks':{'64_byte_wire_length':len(packet),'nominal_brr':355556,'separate_cpp_hook_without_includes':True},'sha256':manifest,'scope':'Static arithmetic/source checks only; no native execution, timing or target linkage assertion'},indent=2))
print(json.dumps({'wire_length':len(packet),'nominal_brr':355556,'files':manifest},indent=2))
