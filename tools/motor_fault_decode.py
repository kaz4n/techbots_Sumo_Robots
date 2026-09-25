# Decodes the exact observed ARM layout of an inert MotorGate diagnostic snapshot.
# Preserves partial and failed states without treating memory bytes as acceptance.
# Independent public-header/ABI fixtures test every reported field and boundary.
import hashlib
import json
import math
from pathlib import Path
import struct

ABI_PATH = Path(__file__).resolve().parents[1] / 'state/analysis/P7_motor_fault_raw/active_abi.json'
ABI_SHA256 = '822c917d32d5bbbcb209ebfad88fd347b516141f85351b84058b3a5ac4ab77a4'
_raw = ABI_PATH.read_bytes()
if hashlib.sha256(_raw).hexdigest() != ABI_SHA256:
    raise ValueError('Motor fault ABI evidence changed')
_ABI = json.loads(_raw)
_PHASES = ('NOT_STARTED', 'DISABLED', 'RUNNING', 'COMPLETE', 'FAULT')
_ENUM_MAX = {'Stage': 2, 'Operation': 4, 'Channel': 3, 'Phase': 4, 'Failure': 5, 'Fault': 6}
_FORMATS = {'u32': '<I', 'u64': '<Q', 'float': '<f', 'bool': '<B'}

# Member kinds come from public C++ declarations; offsets come only from DWARF.
_FIELDS = {
    'motor_fault::Runner': {'attempted_': 'bool', 'last_us_': 'u32', 'equal_polls_': 'u32'},
    'motor_fault::TraceReport': {
        'count': 'u32', 'rejected': 'u32', 'clock_reads': 'u32', 'overflow': 'bool',
        'timing_fault': 'bool', 'has_failure': 'bool', 'has_current': 'bool'},
    'motor_fault::Call': {
        'stage': 'Stage', 'operation': 'Operation', 'channel': 'Channel',
        'application': 'u32', 'requested_high': 'bool', 'period_cycles': 'u32',
        'pulse_cycles': 'u32', 'invoked': 'bool', 'completed': 'bool', 'returned': 'bool',
        'timing_valid': 'bool', 'started_us': 'u32', 'completed_us': 'u32'},
    'motor_fault::Report': {
        'phase': 'Phase', 'failure': 'Failure', 'begin_called': 'bool', 'begin_ok': 'bool',
        'halt_called': 'bool', 'begin_fault': 'Fault', 'applications': 'u32',
        'next_release_us': 'u32', 'missed_releases': 'u32'},
    'motors::MotorGate': {
        'fault_': 'Fault', 'initialized_': 'bool', 'began_': 'bool', 'armed_': 'bool',
        'hold_complete_': 'bool', 'release_us_': 'u32', 'last_token_': 'u64', 'halted_': 'bool'},
    'motors::Result': {'fault': 'Fault', 'consumed': 'bool'},
    'motors::HaltResult': {
        'fresh': 'bool', 'attempted': 'bool', 'inhibition_confirmed': 'bool',
        'timing_valid': 'bool', 'started_us': 'u32', 'completed_us': 'u32', 'fault': 'Fault'},
    'fsm::PreviousTick': {
        'applied_valid': 'bool', 'token': 'u64', 'applied_us': 'u32', 'motors_enabled': 'bool',
        'duty_l': 'float', 'duty_r': 'float', 'duration_valid': 'bool',
        'completed_us': 'u32', 'execution_us': 'u32'},
}


def _offset(type_name, member):
    return _ABI['types'][type_name]['offsets'][member]


def _scalar(blob, offset, kind):
    value = struct.unpack_from(_FORMATS.get(kind, '<B'), blob, offset)[0]
    if kind == 'bool':
        if value not in (0, 1):
            raise ValueError('Nonbinary boolean at byte ' + str(offset))
        return bool(value)
    if kind in _ENUM_MAX and value > _ENUM_MAX[kind]:
        raise ValueError('Invalid ' + kind + ' at byte ' + str(offset))
    if kind == 'float' and not math.isfinite(value):
        raise ValueError('Nonfinite float at byte ' + str(offset))
    return value


def _view(blob, type_name, base):
    return {name: _scalar(blob, base + _offset(type_name, name), kind)
            for name, kind in _FIELDS[type_name].items()}


def _trace(blob):
    base = _offset('motor_fault::Runner', 'trace_') + _offset('motor_fault::Trace', 'report_')
    trace = _view(blob, 'motor_fault::TraceReport', base)
    capacity = _ABI['extents']['calls']
    if trace['count'] > capacity:
        raise ValueError('Trace count exceeds stored capacity')
    start = base + _offset('motor_fault::TraceReport', 'calls')
    stride = _ABI['types']['motor_fault::Call']['size']
    trace['calls'] = [_view(blob, 'motor_fault::Call', start + i * stride) for i in range(capacity)]
    for name in ('current', 'first_failure'):
        trace[name] = _view(blob, 'motor_fault::Call', base + _offset('motor_fault::TraceReport', name))
    return trace


def _report(blob):
    base = _offset('motor_fault::Runner', 'report_')
    report = _view(blob, 'motor_fault::Report', base)
    capacity = _ABI['extents']['applied']
    if report['applications'] > capacity:
        raise ValueError('Application count exceeds stored capacity')
    report['applied'] = []
    start = base + _offset('motor_fault::Report', 'applied')
    stride = _ABI['types']['motors::Result']['size']
    for i in range(capacity):
        position = start + i * stride
        result = _view(blob, 'motors::Result', position)
        result['feedback'] = _view(blob, 'fsm::PreviousTick', position + _offset('motors::Result', 'feedback'))
        report['applied'].append(result)
    report['halt'] = _view(blob, 'motors::HaltResult', base + _offset('motor_fault::Report', 'halt'))
    return report


def decode_snapshot(blob):
    """Decode fixed-layout bytes; DECODED makes no origin/coherence/pass claim."""
    if type(blob) is not bytes or len(blob) != _ABI['types']['motor_fault::Runner']['size']:
        raise ValueError('Expected exactly 2592 immutable bytes')
    report = _report(blob)
    gate_base = _offset('motor_fault::Runner', 'gate_')
    gate = _view(blob, 'motors::MotorGate', gate_base)
    gate['halt_result_'] = _view(blob, 'motors::HaltResult',
                               gate_base + _offset('motors::MotorGate', 'halt_result_'))
    return {'status': 'DECODED', 'schema': 'motor-fault-snapshot-v1', 'coherence': 'UNPROVEN',
            'reported_phase': _PHASES[report['phase']],
            'runner': _view(blob, 'motor_fault::Runner', 0), 'trace': _trace(blob),
            'report': report, 'gate': gate}
