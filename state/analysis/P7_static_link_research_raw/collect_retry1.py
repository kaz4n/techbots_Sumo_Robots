"""Retry source transfer with base64 and inspect only stored loader/tool files.
The original CRLF-altered cat transfer is retained as a failed hash check.
No tool image processor, target, compiler, upload, or inferior is invoked.
"""
import base64
import hashlib
import json
from pathlib import Path
from collect_sources import BIN, CORE, LOADER, OUT, TOOLS, run


def sources():
    hashes = {line.split('  ', 1)[1]: line.split('  ', 1)[0]
              for line in (OUT / 'installed_hashes.stdout').read_text().splitlines()}
    paths = [CORE + '/' + p for p in (
        'variants/_ldscripts/memory-static.ld',
        'variants/_ldscripts/build-static.ld',
        'variants/arduino_uno_q_stm32u585xx/syms-static.ld')]
    for path in paths:
        result = run(Path(path).name + '_base64', ['base64', '--', path])
        assert result.returncode == 0
        content = base64.b64decode(result.stdout)
        assert hashlib.sha256(content).hexdigest() == hashes[path]
        (OUT / Path(path).name).write_bytes(content)
    rg = run('rg_available', ['sh', '-c', 'command -v rg'])
    if rg.returncode == 0:
        args = ['rg', '-n', '--max-count', '20', '--glob', '*.c', '--glob', '*.cpp',
                '--glob', '*.h', '--glob', '!**/llext-edk/**',
                r'\b__wrap_(random|calloc|free|malloc|realloc)\b', CORE]
    else:
        args = ['grep', '-RInE', '--include=*.c', '--include=*.cpp', '--include=*.h',
                '--exclude-dir=llext-edk', r'\b__wrap_(random|calloc|free|malloc|realloc)\b', CORE]
    result = run('wrapper_locations', args)
    assert result.returncode in (0, 1) and len(result.stdout) < 100000


def build_info():
    code = '''import json,mmap,sys
def varint(m,pos):
 value=0; shift=0
 while shift<64:
  b=m[pos]; pos+=1; value|=(b&127)<<shift
  if not b&128:return value,pos
  shift+=7
 raise ValueError('oversized varint')
def string(m,pos):
 size,pos=varint(m,pos)
 assert size<65536 and pos+size<=len(m)
 return m[pos:pos+size].decode('utf-8','replace'),pos+size
for path in sys.argv[1:]:
 with open(path,'rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as m:
  offset=m.find(b'\\xff Go buildinf:')
  row={'path':path,'offset':offset}
  if offset>=0:
   row['header_hex']=m[offset:offset+32].hex()
   if m[offset+15]&2:
    row['go_version'],pos=string(m,offset+32)
    row['module_build_info'],pos=string(m,pos)
   else:row['limitation']='pointer-form build info not decoded'
  print(json.dumps(row))
'''
    result = run('go_build_info', ['python3', '-c', code, *TOOLS])
    assert result.returncode == 0


def loader():
    args = [BIN + 'arm-zephyr-eabi-gdb', '-nx', '-nh', '-batch', LOADER]
    for command in ['info address loader', 'disassemble /r loader',
                    'p/x sketch_base_addr', 'p/x sketch_max_size',
                    'p/x &llext_heap', 'p/x llext_heap.heap.init_bytes']:
        args.extend(['-ex', command])
    result = run('loader_dispatch', args)
    assert result.returncode == 0 and len(result.stdout) < 100000


if __name__ == '__main__':
    sources()
    build_info()
    loader()
