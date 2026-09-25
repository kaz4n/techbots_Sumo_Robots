# Adapts a checked dynamic/Immediate MATCH artifact to the existing uploader.
# Keeps precompiled selection separate from qualification and run permission.
# Independent host tests cover profiles, admission and unchanged lifecycle reuse.
from pathlib import Path
import re
import time


def match_profile(uploader, support, source_sha256, build_id, run_id):
    for name, value, width in (('source', source_sha256, 64),
                               ('build', build_id, 32), ('run', run_id, 32)):
        support.require(type(value) is str and re.fullmatch(
            '[0-9a-f]{' + str(width) + '}', value), 'Invalid MATCH ' + name)
    parent = uploader.PARENT
    sketch = parent + '/' + source_sha256 + '/app'
    run_root = (parent + '/_app_builds/native-app-v1/' + source_sha256 +
                '/match-immediate/' + build_id)
    files = dict(uploader.FILE_PATHS)
    files['raw'] = run_root + '/build/app.ino.elf'
    files['sketch'] = run_root + '/build/app.ino.elf-zsk.bin'
    files['exported'] = run_root + '/artifacts/app.ino.elf-zsk.bin'
    absent = uploader.ABSENT[:-3] + tuple(
        sketch + '/' + name for name in ('sketch.yaml', 'sketch.yml', 'sketch.json'))
    output = parent + '/match-' + source_sha256[:8] + '-' + run_id + '-upload'
    return {'fixed': {'schema': 'fixed-match-upload-v1', 'run_id': run_id,
                      'source_sha256': source_sha256, 'output': output},
            'schema_prefix': 'match-upload-', 'files': files, 'absent': absent,
            'argv': ['/usr/bin/arduino-cli', '--config-file', '/dev/null', 'upload',
                     '--fqbn', 'arduino:zephyr:unoq:wait_linux_boot=no',
                     '--input-file', files['raw'], sketch]}


def _attempt_type(uploader):
    class MatchUpload(uploader.Upload):
        # Only initialization differs: all execution and evidence methods inherit.
        def __init__(self, helper, support, profile, bindings, fs_root, executor, clock):
            self.helper, self.support = helper, support
            self.input_bindings = bindings
            self.run_id = profile['fixed']['run_id']
            self.limit_files = uploader.limit_upload_files
            self.fs_root, self.executor = fs_root, executor
            self.clock = time.monotonic if clock is None else clock
            self.started = self.now()
            self.report = {'schema': 'match-upload-result-v1', 'run_id': None,
                           'source_sha256': profile['fixed']['source_sha256'],
                           'status': 'FAILED', 'attempts': 0,
                           'started_utc': support.utc(), 'finished_utc': None,
                           'started_monotonic': self.started, 'finished_monotonic': None,
                           'subprocess': None, 'stdout': None, 'stderr': None,
                           'first_error': None, 'postcheck_errors': []}
            self.root_fd, self.output_fd = None, None
            self.claimed, self.first_exception = False, None
            self.context_failures = []
            self.process_error = None
            self.profile, self.argv = profile, profile['argv']
    return MatchUpload


def upload_match(helper, support, uploader, *, bindings, source_sha256, build_id,
                 run_id, fs_root=Path('/'), executor=None, clock=None):
    profile = match_profile(uploader, support, source_sha256, build_id, run_id)
    checked = uploader._checked_bindings(support, bindings, profile)
    package, exported = checked['files']['sketch'], checked['files']['exported']
    support.require(all(package[name] == exported[name] for name in ('bytes', 'sha256')),
                    'Build and exported MATCH packages differ')
    attempt = _attempt_type(uploader)(helper, support, profile, checked,
                                      fs_root, executor, clock)
    return uploader._upload(attempt)
