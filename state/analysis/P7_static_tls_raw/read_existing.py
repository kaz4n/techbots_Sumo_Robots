# Reads fixed existing D144 and installed TLS source files without changing them.
# Reuses the tested helper's descriptor, claim and stable-file checks for diagnosis.
# Inspected separately before its one-shot execution; never a build/admission tool.
import base64
import hashlib
import json
import os
import sys
import types
import zlib

if len(sys.argv) != 4 or not sys.dont_write_bytecode:
    raise ValueError('Expected helper, claim and fixed artifact records with -B')
compressed = base64.b64decode(sys.argv[1], validate=True)
decoder = zlib.decompressobj()
source = decoder.decompress(compressed, 98305)
if len(source) > 98304 or not decoder.eof or decoder.unused_data or decoder.unconsumed_tail:
    raise ValueError('Invalid helper framing')
if hashlib.sha256(source).hexdigest() != '8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8':
    raise ValueError('Helper drift')
h = types.ModuleType('fixed_d146_helper')
exec(compile(source, '<fixed-d146-helper>', 'exec'), h.__dict__)
run_id = 'f0220228320c4b2aa20c3e5e8264c813'
claim = h.claim_argument(sys.argv[2], run_id)
expected = h.decode_json(base64.b64decode(sys.argv[3], validate=True))
if set(expected) != set(h.LIMITS):
    raise ValueError('Wrong artifact set')
core = '/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0'
loader = core + '/firmwares/zephyr-arduino_uno_q_stm32u585xx.elf'
tls = core + '/variants/arduino_uno_q_stm32u585xx/tls-syms.S'
root = os.open('/', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
result = {'scope': 'READ_ONLY_TLS_PROVENANCE', 'claim': claim, 'files': {}}


def installed(path, limit):
    parent, name = path.rsplit('/', 1)
    with h.directory(root, parent) as fd:
        raw, identity = h.read_file(fd, name, limit)
    return raw, h.file_record('regular', identity, h.sha256(raw))


def payload(raw, record):
    return dict(record=record, zlib_base64=base64.b64encode(zlib.compress(raw, 9)).decode('ascii'))


try:
    result['identity'] = h.identity(root)
    with h.claimed(root, claim) as fds:
        before = {}
        h.scan_artifacts(fds, before)
        if before['files'] != expected:
            raise ValueError('D144 artifact identity drift')
        loader_raw, loader_record = installed(loader, 16777216)
        if loader_record['sha256'] != '39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd':
            raise ValueError('Packaged firmware drift')
        tls_raw, tls_record = installed(tls, 65536)
        map_record, map_raw = h.observe_file(fds['build'], 'app.ino.map', 16777216)
        if map_record != expected['build/app.ino.map'] or map_raw is None:
            raise ValueError('Map drift')
        result['files']['tls-syms.S'] = payload(tls_raw, tls_record)
        result['files']['app.ino.map'] = payload(map_raw, map_record)
        result['loader'] = loader_record
        # The actual map must name this exact variant object before it is read.
        object_path = h.run_paths(run_id)['build'] + '/core/tls-syms.S.o'
        object_record = None
        if object_path.encode() in map_raw:
            object_raw, object_record = installed(object_path, 1048576)
            result['files']['tls-syms.S.o'] = payload(object_raw, object_record)
        else:
            result['object_unresolved'] = 'Fixed candidate not named in map; no alternative path read'
        # Two original forms have identical content hashes; observe both anyway.
        for name in ('app.ino_debug.elf', 'app.ino_temp.elf'):
            record, raw = h.observe_file(fds['build'], name, 16777216)
            if record != expected['build/' + name] or raw is None:
                raise ValueError('ELF form drift')
            if name.endswith('_temp.elf') and record['sha256'] != expected['build/app.ino_debug.elf']['sha256']:
                raise ValueError('Cannot represent unequal ELF forms with one payload')
            result['files'][name] = payload(raw, record) if name.endswith('_debug.elf') else dict(record=record, same_bytes_as='app.ino_debug.elf')
        closing = [(loader, loader_record), (tls, tls_record)]
        if object_record is not None:
            closing.append((object_path, object_record))
        for path, record in closing:
            _, after = installed(path, 16777216)
            if after != record:
                raise ValueError('Installed/object file changed during observation')
        after = {}
        h.scan_artifacts(fds, after)
        if after['files'] != expected:
            raise ValueError('D144 artifacts changed during observation')
        result['artifact_postcheck'] = after['files']
    if h.identity(root) != result['identity']:
        raise ValueError('Identity changed during observation')
finally:
    os.close(root)
encoded = h.canonical(result)
if len(encoded.encode()) > 2097152:
    raise ValueError('Diagnostic output exceeds 2MiB')
print(encoded)
