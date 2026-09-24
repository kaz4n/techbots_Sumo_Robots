# Validates the existing D144 packet with the exact D147 native TLS extension.
# Keeps structural evidence separate from loading, firmware execution and release.
# Reviewed before one read-only run; frozen validators retain their own host tests.
import base64
import hashlib
import os
import sys
import types
import zlib

HELPER_SHA = '8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8'
VALIDATOR_SHA = 'cd52a29a32b8ae1da4bea51dd55d9011386dd4be0ca537195bb124d13031d6c0'
BASE_SHA = 'd30372dd4b8fb8c2661d00affc4a215cc88e3f62511995ff6303827bed4b7368'
LOADER_SHA = '39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd'
TLS_SHA = '68bb147615813666d528b9bd650e02fb8e240f0db841939e8460d7a52fd2ee70'
RUN_ID = 'f0220228320c4b2aa20c3e5e8264c813'
CORE = '/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0'
LOADER = CORE + '/firmwares/zephyr-arduino_uno_q_stm32u585xx.elf'
TLS = CORE + '/variants/arduino_uno_q_stm32u585xx/tls-syms.S'


def load_inputs():
    if len(sys.argv) != 6 or not sys.dont_write_bytecode:
        raise ValueError('Expected helper, claim, records and two validators with -B')
    compressed = base64.b64decode(sys.argv[1], validate=True)
    if base64.b64encode(compressed).decode('ascii') != sys.argv[1]:
        raise ValueError('Noncanonical helper token')
    decoder = zlib.decompressobj()
    source = decoder.decompress(compressed, 98305)
    if len(source) > 98304 or not decoder.eof or decoder.unused_data or decoder.unconsumed_tail:
        raise ValueError('Invalid helper framing')
    if hashlib.sha256(source).hexdigest() != HELPER_SHA:
        raise ValueError('Helper drift')
    helper = types.ModuleType('fixed_d148_helper')
    exec(compile(source, '<fixed-d148-helper>', 'exec'), helper.__dict__)
    claim = helper.claim_argument(sys.argv[2], RUN_ID)
    raw = helper.decode_base64(sys.argv[3])
    expected = helper.decode_json(raw)
    helper.require(helper.canonical(expected).encode() == raw, 'BAD_REQUEST',
                   'Noncanonical artifact records')
    check_records(helper, expected)
    extension = helper.decode_compressed(sys.argv[4], 32768, VALIDATOR_SHA)
    base = helper.decode_compressed(sys.argv[5], 32768, BASE_SHA)
    namespace = {'__name__': 'fixed_d148_native_artifacts'}
    exec(compile(extension, '<fixed-d148-native-artifacts>', 'exec'), namespace)
    return helper, claim, expected, namespace['validate_artifacts'], base


def check_records(h, expected):
    h.keys(expected, h.LIMITS)
    for name, record in expected.items():
        h.keys(record, ('state', 'identity', 'sha256'))
        h.keys(record['identity'], ('device', 'inode', 'bytes', 'mtime_ns', 'ctime_ns'))
        h.require(record['state'] == 'regular' and
                  all(h.unsigned(value) for value in record['identity'].values()) and
                  0 < record['identity']['bytes'] <= h.LIMITS[name] and
                  type(record['sha256']) is str and h.HEX.fullmatch(record['sha256']),
                  'BAD_REQUEST', 'Invalid expected artifact record')
    h.require(expected['build/app.ino.bin-zsk.bin']['sha256'] ==
              expected['artifacts/app.ino.bin-zsk.bin']['sha256'],
              'BAD_REQUEST', 'Expected exported package hash differs')


def installed(h, root, path, limit, digest):
    parent, name = path.rsplit('/', 1)
    with h.directory(root, parent) as fd:
        raw, identity = h.read_file(fd, name, limit)
    record = h.file_record('regular', identity, h.sha256(raw))
    h.require(record['sha256'] == digest, 'FILE_READ', 'Installed file drift: ' + name)
    return raw, record


def error_record(error):
    return {'class': type(error).__name__, 'message': str(error)}


def postcheck(result, name, function):
    try:
        function()
    except Exception as error:
        result['postcheck_errors'].append(dict(check=name, **error_record(error)))


def validate(h, payloads, tls, base, validator, result):
    inputs = {key.split('/')[1]: raw for key, raw in payloads.items()
              if key.startswith('build/')}
    try:
        report = validator(inputs, tls, base)
        expected = {name: {'bytes': len(raw), 'sha256': h.sha256(raw)}
                    for name, raw in inputs.items()}
        h.require(report['status'] == 'STATIC_NATIVE_TLS_LAYOUT_PACKAGE_PASS' and
                  report['artifacts'] == expected, 'LAYOUT_REJECTED',
                  'Report status or artifact identity differs')
        result['report'] = report
    except Exception as error:
        result['error'] = error_record(error)


def observe(h, root, claim, expected, validator, base, result):
    with h.claimed(root, claim) as fds:
        before = {}
        payloads = h.scan_artifacts(fds, before, keep=True)
        h.require(before['files'] == expected, 'FILE_READ', 'D144 artifact identity drift')
        result['files'] = before['files']
        _, result['loader'] = installed(h, root, LOADER, 16777216, LOADER_SHA)
        tls, result['tls_source'] = installed(h, root, TLS, 65536, TLS_SHA)
        validate(h, payloads, tls, base, validator, result)

        def check_installed(path, limit, digest, original):
            _, after = installed(h, root, path, limit, digest)
            h.require(after == original, 'FILE_READ', 'Installed file identity changed')

        def check_artifacts():
            after = {}
            h.scan_artifacts(fds, after)
            h.require(after['files'] == expected, 'FILE_READ', 'D144 artifacts changed')

        postcheck(result, 'loader', lambda: check_installed(
            LOADER, 16777216, LOADER_SHA, result['loader']))
        postcheck(result, 'tls_source', lambda: check_installed(
            TLS, 65536, TLS_SHA, result['tls_source']))
        postcheck(result, 'files', check_artifacts)


def main():
    h, claim, expected, validator, base = load_inputs()
    result = dict(scope='READ_ONLY_NATIVE_TLS_VALIDATION', claim=claim, identity=None,
                  loader=None, tls_source=None, validator_sha256=VALIDATOR_SHA,
                  base_sha256=BASE_SHA, files={}, report=None, error=None,
                  postcheck_errors=[])
    root = os.open('/', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        try:
            result['identity'] = h.identity(root)
            observe(h, root, claim, expected, validator, base, result)
        except Exception as error:
            if result['error'] is None:
                result['error'] = error_record(error)
            else:
                result['postcheck_errors'].append(dict(check='observation', **error_record(error)))

        def check_identity():
            h.require(h.identity(root) == result['identity'], 'IDENTITY', 'Identity changed')

        def check_claim():
            h.require(h.checked_claim(root, claim) == claim, 'PATH', 'Claim changed')

        postcheck(result, 'identity', check_identity)
        postcheck(result, 'claim', check_claim)
    finally:
        os.close(root)
    encoded = h.canonical(result)
    if len(encoded.encode()) + 1 > 1048576:
        raise ValueError('Validation output exceeds 1MiB')
    print(encoded)
    return 2 if result['error'] is not None or result['postcheck_errors'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
