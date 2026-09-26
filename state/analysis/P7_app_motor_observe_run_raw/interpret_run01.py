# Decodes the saved D195 observation using the current observed ABI02 offsets.
# Preserves raw capture bytes and separates pre-abort from final state.
# Actual field values are independently reviewed against the retained bytes.
import base64
import hashlib
import json
from pathlib import Path
import struct


def digest(body):
    return hashlib.sha256(body).hexdigest()


def main():
    root = Path(__file__).resolve().parent
    packet = root / 'retrieved_inert_run01/0001-read-saved-results/stdout'
    raw = packet.read_bytes()
    assert digest(raw) == '3bb9425f39ba71ef796308e8d94b670158f7785eded44849f7ba82515f4e1c90'
    layout = root.parent / 'P7_app_motor_observe_compile_raw/abi_static02_decode_fields.json'
    layout_raw = layout.read_bytes()
    assert digest(layout_raw) == 'b96b6a3e7349baff471af3bb115c13ab2c1de07c6949a419ed3e9ed1afe16939'
    fields = json.loads(layout_raw)['types']
    aliases = {name.split('::')[-1]: name for name in fields}
    aliases.update(Result='motors::Result', CountdownResult='countdown::Result')
    scalars = {'u8': 'B', 'u16': 'H', 'u32': 'I', 'u64': 'Q', 'f32': 'f', 'bool': 'B'}

    def decode(kind, body, offset=0):
        if kind in scalars:
            value = struct.unpack_from('<' + scalars[kind], body, offset)[0]
            if kind == 'bool':
                assert value in (0, 1), (kind, offset, value)
                return bool(value)
            return value
        if kind == 'Call[64]':
            return [decode('motor_fault::Call', body, offset + i * 32) for i in range(64)]
        name = kind if kind in fields else aliases[kind]
        spec = fields[name]
        assert offset + spec['bytes'] <= len(body)
        return {key: decode(item['kind'], body, offset + item['offset'])
                for key, item in spec['fields'].items()}

    data = json.loads(raw)
    bodies = {}
    for row in data['files']:
        body = base64.b64decode(row['data_base64'], validate=True)
        assert len(body) == row['bytes'] and digest(body) == row['sha256']
        bodies[Path(row['path']).name] = body
    capture = json.loads(bodies['capture_result.json'])
    types = dict(trace='motor_fault::TraceReport', report='app_motor_observe::Report',
                 runtime='app::RuntimeReport', transaction='app::TransactionReport',
                 previous='fsm::PreviousTick', gate='motors::MotorGate')
    windows = {}
    for record in capture['analysis']['snapshots']:
        body = bodies[record['file']]
        assert len(body) == record['bytes'] and digest(body) == record['sha256']
        kind = types[record['name'].split('.')[1]]
        assert len(body) == fields[kind]['bytes']
        windows[record['name']] = decode(kind, body)
    equal = {name: windows['first.' + name] == windows['second.' + name] for name in types}
    result = dict(schema='d195-run01-observed-fields-v1', retrieval_sha256=digest(raw),
                  field_map_sha256=digest(layout_raw), coherence='UNPROVEN',
                  limitation='Selected observed fields only; no atomicity, electrical or WCET claim',
                  repeated_fields_equal=equal, windows=windows)
    output = root / 'retrieved_inert_run01/decoded.json'
    with output.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(result, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')
    print(json.dumps(dict(output=str(output), sha256=digest(output.read_bytes()), repeated=equal)))


if __name__ == '__main__':
    main()
