# Derives one D237 scratch cleanup package from the accepted D236 package.
# Changes fixed identity data only and proves exact reversal to every original.
# Local preparation and controlled fixtures never dispatch native commands.
import ast
import base64
import bz2
import hashlib
import json
from pathlib import Path
import shlex
import subprocess

ROOT = Path(__file__).absolute().parents[3]
OLD = ROOT / 'state/analysis/P7_recorder_six_cleanup_raw'
RAW = Path(__file__).absolute().parent
STAGE = '/home/arduino/sumox26_codex_build/cleanup-recorder-repeat-root01'
ADMISSION_SHA = '18b59196f50a3fb9bc098a74339ee35844cbbe780c0753ea9fa4992328f5a524'


def pin(raw):
    return dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())


def save(name, raw):
    if (RAW / name).exists():
        assert (RAW / name).read_bytes() == raw, 'Changed local preparation output: ' + name
        return
    with (RAW / name).open('xb') as stream:
        stream.write(raw)


def json_bytes(value):
    return (json.dumps(value, indent=2, sort_keys=True) + '\n').encode()


class Derivation:
    def __init__(self, name):
        self.path = OLD / name
        self.original = self.path.read_bytes()
        self.raw = self.original
        self.steps = []

    def replace(self, old, new, count=1):
        old, new = old.encode(), new.encode()
        assert old != new and self.raw.count(old) == count, (self.path.name, old[:120])
        before = pin(self.raw)
        self.raw = self.raw.replace(old, new)
        assert self.raw.count(new) == count
        self.steps.append(dict(old=old.decode(), new=new.decode(), count=count, before=before, after=pin(self.raw)))

    def assignment(self, name, value):
        text = self.raw.decode()
        nodes = [n for n in ast.parse(text).body if isinstance(n, ast.Assign) and len(n.targets) == 1
                 and isinstance(n.targets[0], ast.Name) and n.targets[0].id == name]
        assert len(nodes) == 1
        self.replace(ast.get_source_segment(text, nodes[0].value), repr(value))

    def finish(self, name):
        reversed_raw = self.raw
        for step in reversed(self.steps):
            assert pin(reversed_raw) == step['after']
            assert reversed_raw.count(step['new'].encode()) == step['count']
            reversed_raw = reversed_raw.replace(step['new'].encode(), step['old'].encode())
            assert pin(reversed_raw) == step['before']
        assert reversed_raw == self.original
        save(name, self.raw)
        return dict(template=dict(path=self.path.relative_to(ROOT).as_posix(), pin=pin(self.original)),
                    before=pin(self.original), after=pin(self.raw), steps=self.steps, complete_reverse_equal=True)


def main():
    admission_raw = (RAW / 'admission01.json').read_bytes()
    assert pin(admission_raw)['sha256'] == ADMISSION_SHA
    receipt = json.loads(admission_raw)
    assert receipt['returncode'] == 0 and not receipt['stderr']
    admission = json.loads(receipt['stdout'])
    assert admission['status'] == 'OBSERVED' and admission['first_error'] is None
    assert admission['exact_three_d237_copies'] is True and admission['expected_originals_match'] is True
    assert admission['directory_before'] == admission['directory_after']
    assert admission['directory_before']['dev'] == 34 and admission['directory_before']['ino'] == 7093
    assert all(row['status'] == 'PASS' for row in admission['closing_checks'])
    assert sum(row['bytes'] for row in admission['files'].values()) == 2359784
    recipe = Derivation('cleanup_remoteocd01.py')
    recipe.replace('D233', 'D237')
    recipe.replace('b13a32b5e92993a49f165b907d5d6036fa933e1680bb23ff2738620b294fd584',
                   '3b4812a7a57ec964437d6d1048f96724e3fed5d0a3f9419acd26adbcd5e70a5d')
    recipe.replace('recorder-07f19e32c483ceba/build/recorder.ino.bin-zsk.bin', 'recorder-771c04943d4c4a75/build/recorder.ino.bin-zsk.bin')
    recipe.replace('info.st_ino == 6818', 'info.st_ino == 7093')
    recipe.replace('recorder-six-exact-scratch-cleanup-v1', 'recorder-repeat-exact-scratch-cleanup-v1')
    records = {'recipe': recipe.finish('cleanup_remoteocd01.py')}
    projection_old = b'                except FileNotFoundError:\n                    continue\n'
    projection_new = b'                except FileNotFoundError:\n                    raise\n'
    assert recipe.raw.count(projection_old) == 1
    projected = recipe.raw.replace(projection_old, projection_new)
    wrapper = Derivation('cleanup_root01.py')
    wrapper.replace('cleanup-recorder-six-root01', 'cleanup-recorder-repeat-root01')
    wrapper.replace("(7722, '14cc1ff962fa8f8e4366f0ee5e3e4ae41f2fa5e33b8c482613901b91d71ed402')",
                    repr((len(recipe.raw), pin(recipe.raw)['sha256'])))
    wrapper.replace('a35bd5006f26fa37fe106eff775a57c40d0d0c55979ccd6b0a4451dfb6f1a3e8', pin(projected)['sha256'])
    wrapper.replace('recorder-six-authenticated-scratch-cleanup-v1', 'recorder-repeat-authenticated-scratch-cleanup-v1')
    records['wrapper'] = wrapper.finish('cleanup_root01.py')
    helper_path = ROOT / 'state/analysis/P7_static_link_probe_raw/static_remote.py'
    helper = helper_path.read_bytes()
    assert pin(helper) == dict(bytes=33321, sha256='8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8')
    packet = {'cleanup_root01.py': wrapper.raw.decode(), 'cleanup_remoteocd01.py': recipe.raw.decode(), 'static_remote.py': helper.decode()}
    pins = {name: pin(body.encode()) for name, body in packet.items()}
    token = base64.b64encode(bz2.compress(json.dumps(packet, separators=(',', ':')).encode(), 9)).decode()
    records['program_derivations'] = {}
    intents = {}
    for kind in ('absence', 'stage', 'verify', 'retrieve'):
        program = Derivation(kind + '_program01.py')
        program.assignment('pins', pins)
        tree = ast.parse(program.raw.decode())
        node = next(n for n in tree.body if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name) and n.targets[0].id == 'packet')
        strings = [n.value for n in ast.walk(node.value) if isinstance(n, ast.Constant) and isinstance(n.value, str) and len(n.value) > 1000]
        assert len(strings) == 1
        program.replace(strings[0], token)
        program.replace('cleanup-recorder-six-root01', 'cleanup-recorder-repeat-root01',
                        {'absence': 2, 'stage': 3, 'verify': 1, 'retrieve': 1}[kind])
        if kind in ('absence', 'stage'):
            program.replace('info.st_ino==6818', 'info.st_ino==7093')
        if kind == 'verify':
            program.assignment('expected_scratch', admission['directory_before'])
            program.assignment('expected_copies', {name: {k: row[k] for k in ('identity', 'sha256')} for name, row in admission['files'].items()})
        if kind in ('verify', 'retrieve'):
            program.assignment('expected_originals', admission['originals'])
            program.replace('recorder-six-independent-', 'recorder-repeat-independent-')
        records['program_derivations'][kind] = program.finish(kind + '_program01.py')
        original_intent = OLD / ('cleanup_' + kind + '_intent01.json')
        intent = json.loads(original_intent.read_bytes())
        intent.update(stage=STAGE, source_pins=pins, program=pin(program.raw),
                      schema=intent['schema'].replace('recorder-six-cleanup-', 'recorder-repeat-cleanup-'),
                      template=dict(path=original_intent.relative_to(ROOT).as_posix(), pin=pin(original_intent.read_bytes())))
        if kind in ('absence', 'stage'):
            remote = shlex.split(intent['argv'][-1]);remote[-1] = program.raw.decode()
            intent['argv'][-1] = shlex.join(remote)
            intent['command_units'] = len(subprocess.list2cmdline(intent['argv']).encode('utf-16-le')) // 2 + 1
            assert intent['command_units'] < 30000
        save('cleanup_' + kind + '_intent01.json', json_bytes(intent));intents[kind] = pin(json_bytes(intent))
    auth_path = OLD / 'cleanup_authenticated_intent01.json'
    auth = json.loads(auth_path.read_bytes())
    auth.update(stage=STAGE, recipe=pin(recipe.raw), wrapper=pin(wrapper.raw), admission=pin(admission_raw),
                result=STAGE + '/result_root01.json', schema='recorder-repeat-cleanup-authenticated-intent-v1',
                template=dict(path=auth_path.relative_to(ROOT).as_posix(), pin=pin(auth_path.read_bytes())))
    auth['argv'][-1] = auth['argv'][-1].replace('cleanup-recorder-six-root01', 'cleanup-recorder-repeat-root01')
    save('cleanup_authenticated_intent01.json', json_bytes(auth));intents['authenticate'] = pin(json_bytes(auth))
    dispatch = Derivation('native_dispatch_template01.py')
    dispatch.replace('D233', 'D237')
    assert ROOT.as_posix() == 'C:/Users/narut/OneDrive/Desktop/Project/techbots_Sumo_Robots'
    dispatch.replace('P7_recorder_six_cleanup_raw', 'P7_recorder_repeat_cleanup_raw')
    dispatch.replace('P7_recorder_six_cleanup_review.md', 'P7_recorder_repeat_cleanup_review.md')
    dispatch.replace('d233-native-dispatch-v1', 'd237-native-dispatch-v1')
    records['dispatcher'] = dispatch.finish('native_dispatch_template01.py')
    records.update(schema='recorder-repeat-cleanup-data-only-derivation-v1', status='PREPARATION_ONLY',
                   admission=pin(admission_raw), helper=dict(path=helper_path.relative_to(ROOT).as_posix(), pin=pin(helper)),
                   projected_recipe=pin(projected), intents=intents)
    save('cleanup_derivation01.json', json_bytes(records))
    print(json.dumps({k: records[k]['after'] for k in ('recipe', 'wrapper', 'dispatcher')}, indent=2))


if __name__ == '__main__':
    main()
