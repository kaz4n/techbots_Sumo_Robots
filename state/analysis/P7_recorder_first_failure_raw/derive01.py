# Projects the reviewed D230 tools onto the single D233 recorder image.
# Changes only exact identity, file inventory and first-failure layout data.
# Reverse proofs and focused host fixtures preserve the existing execution paths.
import hashlib
import json
from pathlib import Path
import types

ROOT = Path(__file__).absolute().parents[3]
RAW = Path(__file__).absolute().parent
COMPILE = 'state/analysis/P7_recorder_delivery_raw/recorder-07f19e32c483ceba'
PINS = {
    'abi': (23716, '2191e8d77513ee3b2d9f47497523cf3199a70112e325e01d1543b8e3aca1add6'),
    'capture': (11767, '13fc387d0cb6d0475232aa4683bf47423ad2f85255db543f62da71ea5c8420b2'),
    'caller': (19572, 'c61858ba7cd940499a9a69ea6a9fc92556e32263bfa54abb13dba5f8d577a87e'),
}


def pin(raw):
    return dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())


def save(name, raw):
    path = ROOT / name
    if path.exists():
        assert path.read_bytes() == raw, name
    else:
        with path.open('xb') as stream:
            stream.write(raw)


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True) + '\n').encode()


def main():
    records = {}
    for kind, oldname, newname in (
            ('abi', 'recorder_failure_abi.py', 'recorder_first_failure_abi.py'),
            ('capture', 'recorder_failure_capture.py', 'recorder_first_failure_capture.py'),
            ('caller', 'run_recorder_failure_capture.py', 'run_recorder_first_failure_capture.py')):
        original = (ROOT / 'tools' / oldname).read_bytes()
        assert (len(original), pin(original)['sha256']) == PINS[kind]
        raw, steps = original, []

        def replace(old, new, count):
            nonlocal raw
            old, new = old.encode(), new.encode()
            assert raw.count(old) == count and old != new, (kind, old, count, raw.count(old))
            raw = raw.replace(old, new)
            assert raw.count(new) == count, (kind, new)
            steps.append(dict(old=old.decode(), new=new.decode(), count=count))

        common = [
            ('recorder_failure', 'recorder_first_failure'),
            ('P7_recorder_failure', 'P7_recorder_first_failure'),
            ('004dc7cff534896a851901f9d7d0ba6066cae060', 'ce4e69390d21d9a91231581a186be4a63213135e'),
            ('377911abefabd094971ee6d089326604', '07f19e32c483cebadecaa63f4d6d720f'),
            ('recorder-377911abefabd094', 'recorder-07f19e32c483ceba'),
            ('3997245574426120340', '572412568535289530'),
            ('702ad99ee4f888c58de1715cb91512cb0a174a646d914db6ce9155489ffa63e8',
             '29cb1e76193e4b7c562d1fd842039f61367a82c2651a2303c09518d35a0c7ce9'),
            ('D230', 'D233'), ('D228 ELF', 'D233 ELF'),
        ]
        for old, new in common:
            count = raw.count(old.encode())
            if count:
                replace(old, new, count)
        if kind == 'abi':
            replace("'recorder::dump::Report', 'recorder::dump::UnoQDumpPort', 'bool')",
                    "'recorder::dump::Report', 'recorder::dump::UnoQDumpPort', 'bool',\n         'recorder::dump::FailureRecord')", 1)
            replace("    'native_status': ('native_dump', 'status_', None),",
                    "    'first_failure': ('native_dump', 'first_failure_', TYPES[8]),\n    'native_status': ('native_dump', 'status_', None),", 1)
            replace("    'app::Fault': 'NONE SETUP ORDER CLOCK IDENTITY RECEIPT ABORTED'.split(),",
                    "    'app::Fault': 'NONE SETUP ORDER CLOCK IDENTITY RECEIPT ABORTED'.split(),\n"
                    "    'recorder::dump::FailureSite': 'NONE SETUP SETUP_OWNERSHIP SETUP_READY FIFO_OWNERSHIP FIFO_READBACK WRITE_POISONED WRITE_CONTEXT WRITE_OWNERSHIP WRITE_ARGUMENT TRANSMIT_OWNERSHIP TRANSMIT_READY TRANSMIT_DEADLINE STORE_DEADLINE COMPLETE_OWNERSHIP COMPLETE_READY COMPLETE_DEADLINE TC_DEADLINE CANCEL REPEATED_BEGIN'.split(),\n"
                    "    'recorder::dump::CleanupDisposition': 'NOT_ATTEMPTED SKIPPED_POISONED SKIPPED_CONTEXT SKIPPED_OWNERSHIP VERIFIED READBACK_FAILED'.split(),", 1)
            marker = "FIELDS += [(x, '', 1, 'bool') for x in WINDOWS if x.startswith('native_') and x != 'native_status']"
            replace(marker, marker + "\nFIELDS += [('first_failure', 'reason', 1, 'recorder::dump::NativeStatus'),\n"
                    "           ('first_failure', 'site', 1, 'recorder::dump::FailureSite'),\n"
                    "           ('first_failure', 'cleanup', 1, 'recorder::dump::CleanupDisposition'),\n"
                    "           ('first_failure', 'cleanup_ownership', 1, 'recorder::dump::NativeStatus')]\n"
                    "FIELDS += [('first_failure', x, 1, 'uint') for x in ('packet_offset', 'packet_size', 'payload_size')]\n"
                    "FIELDS += [('first_failure', 'ownership_evaluated', 1, 'bool')]", 1)
            replace('144', '145', 2)
            replace('== 109', '== 110', 1)
        if kind == 'capture':
            replace('55104', '55376', 3)
            replace('91b6042a3f13e3650fc4b23892f88e69d4c0c56edebd6514662fa2d8cd8208c6',
                    'b13a32b5e92993a49f165b907d5d6036fa933e1680bb23ff2738620b294fd584', 1)
        if kind == 'caller':
            capture = (ROOT / 'tools/recorder_first_failure_capture.py').read_bytes()
            replace('len(source) == 11767', 'len(source) == ' + str(len(capture)), 1)
            replace(PINS['capture'][1], pin(capture)['sha256'], 1)
        reversed_raw = raw
        for step in reversed(steps):
            assert reversed_raw.count(step['new'].encode()) == step['count']
            reversed_raw = reversed_raw.replace(step['new'].encode(), step['old'].encode())
        assert reversed_raw == original
        path = 'tools/' + newname
        save(path, raw)
        records[kind] = dict(template='tools/' + oldname, before=pin(original), path=path,
                             after=pin(raw), steps=steps, complete_reverse_equal=True)
    module = types.ModuleType('fresh_abi_projection')
    module.__file__ = str(ROOT / records['abi']['path'])
    exec(compile((ROOT / records['abi']['path']).read_bytes(), module.__file__, 'exec'), module.__dict__)
    plan = dict(schema='recorder-failure-plan-v1', compile_head=module.COMPILE_HEAD,
                attempt=module.ATTEMPT, source_sha256=module.SOURCE, expressions=module.expressions(),
                compile_records={name: pin((ROOT / COMPILE / name).read_bytes())
                                 for name in ('inputs.json', 'result.json', 'artifacts.json', 'staged_files.json')})
    save('state/analysis/P7_recorder_first_failure_raw/plan.json', encoded(plan))
    save('state/analysis/P7_recorder_first_failure_raw/derivation01.json', encoded(records))
    print(json.dumps({k: v['after'] for k, v in records.items()}, indent=2))


if __name__ == '__main__':
    main()
