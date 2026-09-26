# Projects accepted D233 tools onto one fresh six-store recorder image.
# Fixed identity literals and one bounded uint32 packet-start window change.
# Complete reverse proofs and focused composition tests retain every guard.
import hashlib
import json
from pathlib import Path
import types

ROOT = Path(__file__).absolute().parents[3]
RAW = Path(__file__).absolute().parent
COMPILE = 'state/analysis/P7_recorder_delivery_raw/recorder-771c04943d4c4a75'
PINS = {
    'abi': (24804, '0a2c745275e47d5c89ff0bb5e711d140268bc0d35f78cb0b36e717bbdf75cefb'),
    'capture': (11772, '576efd496802c5d789ce1a6c183144dadb6d309487709d3a0a4fdd4fcb8a1b96'),
    'caller': (19614, 'c5ea40f9583beee040395030a0f73f0f5c50701e0885267fa17205b1319f047a'),
}
REPLACEMENTS = (
    ('recorder_first_failure', 'recorder_six_result'),
    ('ce4e69390d21d9a91231581a186be4a63213135e', '1b2af246cd88e6207e846ee340f8c4e46a5bb980'),
    ('07f19e32c483cebadecaa63f4d6d720f', '771c04943d4c4a759055d794fa4b706e'),
    ('recorder-07f19e32c483ceba', 'recorder-771c04943d4c4a75'),
    ('572412568535289530', '8582740024591403637'),
    ('29cb1e76193e4b7c562d1fd842039f61367a82c2651a2303c09518d35a0c7ce9',
     '289300a4be9547cd294dc1f753bbe17a429d16776c46467fec5417b1290f4ffc'),
    ('b13a32b5e92993a49f165b907d5d6036fa933e1680bb23ff2738620b294fd584',
     '3b4812a7a57ec964437d6d1048f96724e3fed5d0a3f9419acd26adbcd5e70a5d'),
    ('D233', 'D238'),
)


def pin(raw):
    return dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())


def save(path, raw):
    if path.exists():
        assert path.read_bytes() == raw, path
    else:
        with path.open('xb') as stream:
            stream.write(raw)


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True) + '\n').encode()


def main():
    records = {}
    for kind, basename in (('abi', 'recorder_first_failure_abi.py'),
                           ('capture', 'recorder_first_failure_capture.py'),
                           ('caller', 'run_recorder_first_failure_capture.py')):
        original = (ROOT / 'tools' / basename).read_bytes()
        assert (len(original), pin(original)['sha256']) == PINS[kind]
        raw, steps = original, []

        def replace(old, new):
            nonlocal raw
            before, after = old.encode(), new.encode()
            count = raw.count(before)
            assert count and before != after
            raw = raw.replace(before, after)
            assert raw.count(after) == count
            steps.append(dict(old=old, new=new, count=count))

        for old, new in REPLACEMENTS:
            if old.encode() in raw:
                replace(old, new)
        if kind == 'abi':
            marker = "    'session': ('runner', 'session_', None),"
            replace(marker, marker + "\n    'packet_started_us': ('native_dump', 'started_us_', None),")
            marker = "FIELDS += [('session', '', 8, 'uint'), ('native_status', '', 1, 'recorder::dump::NativeStatus')]"
            replace(marker, marker + "\nFIELDS += [('packet_started_us', '', 4, 'uint')]")
        if kind == 'caller':
            capture = (ROOT / 'tools/recorder_six_result_capture.py').read_bytes()
            replace('len(source) == 11772', 'len(source) == ' + str(len(capture)))
            replace(PINS['capture'][1], pin(capture)['sha256'])
        reverse = raw
        for step in reversed(steps):
            assert reverse.count(step['new'].encode()) == step['count']
            reverse = reverse.replace(step['new'].encode(), step['old'].encode())
        assert reverse == original
        name = 'tools/' + basename.replace('recorder_first_failure', 'recorder_six_result')
        save(ROOT / name, raw)
        records[kind] = dict(template='tools/' + basename, path=name, before=pin(original),
                             after=pin(raw), steps=steps, complete_reverse_equal=True)
    module = types.ModuleType('six_result_projection')
    module.__file__ = str(ROOT / records['abi']['path'])
    exec(compile((ROOT / records['abi']['path']).read_bytes(), module.__file__, 'exec'), module.__dict__)
    plan = dict(schema='recorder-failure-plan-v1', compile_head=module.COMPILE_HEAD,
                attempt=module.ATTEMPT, source_sha256=module.SOURCE, expressions=module.expressions(),
                compile_records={name: pin((ROOT / COMPILE / name).read_bytes())
                                 for name in ('inputs.json', 'result.json', 'artifacts.json', 'staged_files.json')})
    save(RAW / 'plan.json', encoded(plan))
    save(RAW / 'derivation01.json', encoded(records))
    print(json.dumps({kind: record['after'] for kind, record in records.items()}, indent=2))


if __name__ == '__main__':
    main()
