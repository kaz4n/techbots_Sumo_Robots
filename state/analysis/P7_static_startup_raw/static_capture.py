# Plans and interprets the fixed current static-image startup observation.
# Refuses unrelated flash or malformed prefixes before claiming sampled progress.
# Independent contract tests cover byte identity, literal layouts and wrap bounds.

_RUNTIME_PHASES = ('NOT_STARTED', 'RUNNING', 'STOPPED', 'FAULT', 'STOP_OBSERVING')
_RUNTIME_FAULTS = ('NONE', 'PORT', 'CLOCK', 'SERVICE_LIMIT', 'TRANSACTION', 'PROJECTION')
_TRANSACTION_PHASES = ('NOT_INITIALIZED', 'IDLE', 'ACQUIRING', 'DECIDED', 'FAULT')
_TRANSACTION_FAULTS = ('NONE', 'SETUP', 'ORDER', 'CLOCK', 'IDENTITY', 'RECEIPT', 'ABORTED')
_RUNTIME_FLAGS = ('fresh', 'initialization_complete', 'raw_lines', 'imu_expired',
                  'calibration_interrupted')
_TRANSACTION_FLAGS = ('decision_made', 'finished', 'timing_valid')
_RUNTIME_WORDS = ('next_release_us', 'missed_releases', 'epochs', 'service_passes',
                  'maximum_execution_us')
_TRANSACTION_WORDS = ('started_us', 'decision_us', 'completed_us', 'execution_us')


def _flash_plan(label, address, length):
    return tuple((label + '.' + str(index), address + offset,
                  min(65536, length - offset))
                 for index, offset in enumerate(range(0, length, 65536)))


def read_plan():
    """Return the exact finite address list; this function performs no reads."""
    return (_flash_plan('before.loader', 0x08000000, 263680)
            + _flash_plan('before.sketch', 0x08100000, 93096)
            + (('first.runtime', 0x2003bc98, 28),
               ('first.transaction', 0x2003b2b0, 24),
               ('second.runtime', 0x2003bc98, 28),
               ('second.transaction', 0x2003b2b0, 24))
            + _flash_plan('after.sketch', 0x08100000, 93096)
            + _flash_plan('after.loader', 0x08000000, 263680))


def _validate(reads, loader, sketch):
    for value, size in ((loader, 263680), (sketch, 93096)):
        if type(value) is not bytes or len(value) != size:
            raise ValueError('Reference must be exact bytes of the fixed length')
    plan = read_plan()
    if not isinstance(reads, (list, tuple)) or len(reads) != len(plan):
        raise ValueError('Capture must contain exactly the planned reads')
    for item, (name, address, size) in zip(reads, plan):
        if not isinstance(item, (list, tuple)) or len(item) != 3:
            raise ValueError('Each read must be a list or tuple of three fields')
        if type(item[0]) is not str or item[0] != name:
            raise ValueError('Read name or order differs')
        if type(item[1]) is not int or item[1] != address:
            raise ValueError('Read address differs')
        if type(item[2]) is not bytes or len(item[2]) != size:
            raise ValueError('Read data must be exact bytes of the planned length')


def _prefix(blob, label, phases, faults, flags, words, errors):
    sample = {'phase': blob[0], 'fault': blob[1], 'raw_hex': blob.hex()}
    for field, names in (('phase', phases), ('fault', faults)):
        value = sample[field]
        sample[field + '_name'] = names[value] if value < len(names) else 'UNKNOWN'
        if value >= len(names):
            errors.append(label + '.' + field)
    for offset, field in enumerate(flags, 2):
        sample[field] = blob[offset]
        if blob[offset] not in (0, 1):
            errors.append(label + '.' + field)
    for offset, field in enumerate(words):
        start = 8 + 4 * offset
        sample[field] = int.from_bytes(blob[start:start + 4], 'little')
    return sample


def _diagnostics(reads, result):
    for index in range(2):
        runtime, transaction = reads[7 + index * 2][2], reads[8 + index * 2][2]
        result['runtime'].append(_prefix(
            runtime, 'runtime[' + str(index) + ']', _RUNTIME_PHASES,
            _RUNTIME_FAULTS, _RUNTIME_FLAGS, _RUNTIME_WORDS, result['errors']))
        result['transaction'].append(_prefix(
            transaction, 'transaction[' + str(index) + ']', _TRANSACTION_PHASES,
            _TRANSACTION_FAULTS, _TRANSACTION_FLAGS, _TRANSACTION_WORDS, result['errors']))


def _classify(result):
    if result['errors']:
        return 'MALFORMED_SAMPLES'
    samples = result['runtime'] + result['transaction']
    if any(s['fault'] != 0 or s['phase_name'] == 'FAULT' for s in samples):
        return 'SAMPLED_FAULT'
    if all(s['phase_name'] == 'RUNNING' for s in result['runtime']):
        delta = (result['runtime'][1]['epochs'] - result['runtime'][0]['epochs']) & 0xffffffff
        result['epoch_delta'] = delta
        if 0 < delta < 0x80000000:
            return 'RUNNING_COUNTER_ADVANCED'
    return 'NO_RUNNING_PROGRESS'


def analyze_capture(reads, expected_loader, expected_sketch):
    """Interpret supplied bytes only; reference provenance belongs to the caller."""
    _validate(reads, expected_loader, expected_sketch)
    flash = {}
    for name, start, stop, expected in (
            ('before_loader', 0, 5, expected_loader),
            ('before_sketch', 5, 7, expected_sketch),
            ('after_loader', 13, 18, expected_loader),
            ('after_sketch', 11, 13, expected_sketch)):
        flash[name] = b''.join(item[2] for item in reads[start:stop]) == expected
    result = dict(flash=flash, observation='FLASH_MISMATCH', runtime=[],
                  transaction=[], epoch_delta=None, errors=[])
    # Fixed addresses are meaningful only after both image brackets agree.
    if all(flash.values()):
        _diagnostics(reads, result)
        result['observation'] = _classify(result)
    return result
