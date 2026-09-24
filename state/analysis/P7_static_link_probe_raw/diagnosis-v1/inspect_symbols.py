# Inspects the single collected D144 ELF without changing admission or its bytes.
# Separates observed symbol encodings from structural or runtime acceptance.
# Cross-checked against GNU readelf output retained by this one-file diagnostic.
from pathlib import Path
import hashlib
import json
import struct
import subprocess

base = Path(__file__).resolve().parent
path = base / 'app.ino.elf'
data = path.read_bytes()
expected = '5cc2dfdec597f1421d6250936569bc113542723c362786f23be62834b5ba0386'
if len(data) != 170616 or hashlib.sha256(data).hexdigest() != expected:
    raise ValueError('Diagnostic ELF drift')
offset = struct.unpack_from('<I', data, 32)[0]
width, count = struct.unpack_from('<HH', data, 46)
sections = [struct.unpack_from('<10I', data, offset + i * width) for i in range(count)]
rejected, encodings = [], {}
for table in sections:
    if table[1] != 2:
        continue
    strings = sections[table[6]]
    pool = data[strings[4]:strings[4] + strings[5]]
    for index in range(table[5] // table[9]):
        name, value, size, info, other, section = struct.unpack_from(
            '<IIIBBH', data, table[4] + index * table[9])
        binding, kind = info >> 4, info & 15
        key = f'bind={binding},type={kind},other={other}'
        encodings[key] = encodings.get(key, 0) + 1
        if binding not in (0, 1, 2) or kind not in (0, 1, 2, 3, 4) or other > 3:
            rejected.append(dict(index=index, name=pool[name:pool.index(0, name)].decode(),
                                 value=hex(value), size=size, bind=binding, type=kind,
                                 other=other, section=section))
relative = path.relative_to(Path.cwd()).as_posix()
command = ['wsl', '-d', 'Ubuntu', '--', 'readelf', '-hSWlrs', relative]
observed = subprocess.run(command, capture_output=True, text=True, check=False)
if observed.returncode != 0:
    raise RuntimeError(observed.stderr)
with (base / 'readelf.txt').open('x', encoding='utf-8') as stream:
    stream.write(observed.stdout)
version = subprocess.run(['wsl', '-d', 'Ubuntu', '--', 'readelf', '--version'],
                         capture_output=True, text=True, check=True).stdout.splitlines()[0]
report = dict(scope='Diagnostic only; frozen validator and negative result unchanged',
              elf_sha256=expected, bytes=len(data), symbol_count=sum(encodings.values()),
              encodings=encodings, rejected=rejected, command=command,
              returncode=observed.returncode, stderr=observed.stderr, tool_version=version)
with (base / 'symbols.json').open('x', encoding='utf-8') as stream:
    json.dump(report, stream, indent=2)
print(json.dumps(dict(symbols=report['symbol_count'], rejected=len(rejected),
                      tool=version, readelf_bytes=len(observed.stdout.encode()))))
