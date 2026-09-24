"""Prepare a bounded second proposal only; no compiler, stage or production edit."""
from pathlib import Path
import difflib
import hashlib
import json
import subprocess

out = Path(__file__).resolve().parent
root = out.parents[2]
folder = out / 'candidate2'
folder.mkdir(exist_ok=True)
names = ['src/core/edge.h', 'src/core/edge.cpp', 'src/core/fsm_robot.cpp', 'src/core/openers.cpp']
texts = {}
for name in names:
    source = out / 'candidate' / name
    texts[name] = (source if source.exists() else root / name).read_text()
old = '''        Result result = terminal(exit_);
#if SUMOX_P5_ABORT_TIMING
        result.abort = abort;
#endif
        return result;'''
new = '''#if SUMOX_P5_ABORT_TIMING
        Result result = terminal(exit_);
        result.abort = abort;
        return result;
#else
        return terminal(exit_);
#endif'''
assert texts['src/core/openers.cpp'].count(old) == 1
texts['src/core/openers.cpp'] = texts['src/core/openers.cpp'].replace(old, new)
old = '''    if (core::modeAvailable(running_mode_)) {
        if (running_mode_ == core::Mode::DIRECT) {
            started = direct_.start(tick_.t_us, result_.heading.heading_deg,
                                     result_.lifecycle.services.opponent_snapshot);
        } else if (running_mode_ == core::Mode::WAIT) {
            started = wait_.start(tick_.t_us, result_.heading.heading_deg);
        } else {
            started = flank_.start(tick_.t_us, result_.heading.heading_deg,
                                    result_.heading.imu_ok, running_mode_);
        }
    }'''
new = '''    // Admission and dispatch share one mode selection; rejected modes call no script.
    switch (running_mode_) {
    case core::Mode::DIRECT:
        started = direct_.start(tick_.t_us, result_.heading.heading_deg,
                                result_.lifecycle.services.opponent_snapshot);
        break;
    case core::Mode::WAIT:
        if constexpr (core::modeAvailable(core::Mode::WAIT))
            started = wait_.start(tick_.t_us, result_.heading.heading_deg);
        break;
    case core::Mode::ARC_R:
    case core::Mode::ARC_L:
        if constexpr (!core::modeAvailable(core::Mode::ARC_R)) break;
        [[fallthrough]];
    case core::Mode::SIDESTEP_R:
    case core::Mode::SIDESTEP_L:
        started = flank_.start(tick_.t_us, result_.heading.heading_deg,
                               result_.heading.imu_ok, running_mode_);
        break;
    default: break;
    }'''
assert texts['src/core/fsm_robot.cpp'].count(old) == 1
texts['src/core/fsm_robot.cpp'] = texts['src/core/fsm_robot.cpp'].replace(old, new)
manifest = {'base_source_commit': '2d924f1f6726920ff515529b6d50a47fb81366ff',
            'scope': 'proposal only; candidate2 has not been compiled or staged', 'files': {}}
diff = []
incremental = []
for name in names:
    path = folder / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(texts[name].encode('utf-8'))
    original = (root / name).read_text()
    committed = subprocess.run(['git', 'show', '2d924f1f:' + name], cwd=root,
                               capture_output=True, check=True).stdout.decode().replace('\r\n', '\n')
    assert original == committed, name
    previous = out / 'candidate' / name
    prior = previous.read_text() if previous.exists() else original
    diff.extend(difflib.unified_diff(original.splitlines(True), texts[name].splitlines(True),
                                   fromfile='a/' + name, tofile='b/' + name))
    incremental.extend(difflib.unified_diff(prior.splitlines(True), texts[name].splitlines(True),
                                   fromfile='candidate1/' + name, tofile='candidate2/' + name))
    manifest['files'][name] = {'base_sha256': hashlib.sha256((root / name).read_bytes()).hexdigest(),
        'candidate_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'bytes': path.stat().st_size}
(out / 'candidate2.patch').write_text(''.join(diff))
(out / 'candidate2_incremental.patch').write_text(''.join(incremental))
manifest['patch_sha256'] = hashlib.sha256((out / 'candidate2.patch').read_bytes()).hexdigest()
(out / 'candidate2_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(json.dumps(manifest, indent=2))
