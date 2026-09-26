# Executes the one independently admitted cleanup with protected console input.
# Keeps the credential out of commands, files and saved diagnostic output.
# The exact saved command and all reviewed inputs are checked before dispatch.
import datetime
import getpass
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
RAW = Path(__file__).resolve().parent


def pin(path):
    body = path.read_bytes()
    return dict(bytes=len(body), sha256=hashlib.sha256(body).hexdigest())


def main():
    assert sys.flags.isolated and sys.dont_write_bytecode and len(sys.argv) == 1
    intent_path = RAW / 'cleanup_authenticated_intent01.json'
    review = ROOT / 'state/reviews/P7_b4_app_cleanup_stage_review.md'
    assert pin(intent_path)['sha256'] == 'bed4004a546117605cbd0f9936f589c7e483194541d49914253f72a0c6194ffc'
    assert pin(review)['sha256'] == '46e3db7745b6b2cead119235cd62a1682063abf9038a8581b18a42d0e7984a6d'
    intent = json.loads(intent_path.read_bytes())
    expected = {
        RAW / 'cleanup_root07.py': intent['wrapper'],
        RAW / 'cleanup_remoteocd06.py': intent['recipe'],
        RAW / 'cleanup_stage_verification01.json': intent['staged_verification'],
        ROOT / 'state/reviews/P7_b4_app_cleanup_preparation_review.md': intent['source_review'],
        ROOT / 'state/reviews/P7_b4_app_cleanup_verifier_preparation_review.md': intent['verifier_review'],
        intent_path: pin(intent_path), review: pin(review),
    }
    assert all(pin(path) == value for path, value in expected.items())
    assert pin(Path(intent['argv'][0]))['sha256'] == 'e79dc8fc3c6385192bdccd7ff7eabe3d5c1ec292475a06b04d82759f07655982'
    record = dict(schema='d220-authenticated-cleanup-transport-v1',
                  intent=pin(intent_path), review=pin(review),
                  started=datetime.datetime.now().astimezone().isoformat(),
                  credential_transport='No-echo console to native stdin only; value omitted',
                  first_error=None)
    with (RAW / 'cleanup_authenticated_invocation01.json').open('x', encoding='utf8') as stream:
        json.dump(record, stream, indent=2)
    credential = getpass.getpass('Board cleanup authentication: ')
    start = time.monotonic()
    try:
        result = subprocess.run(intent['argv'], input=(credential + '\n').encode(),
                                capture_output=True, timeout=70)
        record.update(returncode=result.returncode, stdout=result.stdout.decode(),
                      stderr=result.stderr.decode())
    except Exception as error:
        record['first_error'] = dict(type=type(error).__name__, message=str(error))
    finally:
        del credential
        record['elapsed_seconds'] = time.monotonic() - start
        record['local_input_closure'] = all(pin(path) == value for path, value in expected.items())
        with (RAW / 'cleanup_authenticated_transport01.json').open('x', encoding='utf8') as stream:
            json.dump(record, stream, indent=2)
    print(json.dumps({key: record.get(key) for key in
                      ('returncode', 'first_error', 'elapsed_seconds', 'local_input_closure')}))
    return int(record.get('returncode') != 0 or record['first_error'] is not None
               or not record['local_input_closure'])


if __name__ == '__main__':
    sys.exit(main())
