# Observes ordinary application ABI from the exact inhibited static ELF files.
# Preserves bounded file-only execution without inventing diagnostic snapshots.
# Independent D209 fixtures cover the retained guards and ordinary object schema.
import base64
import hashlib
import os
from pathlib import Path
import re
import stat
import sys
import types

ROOT = Path(__file__).absolute().parents[3]
BASE = 'state/analysis/P7_app_motor_fault_compile_raw/inspect_static_abi.py'
GUARDS = 'state/analysis/P7_motor_const_compile_raw/inspect_static_abi.py'
CONTRACT = 'state/analysis/P7_ordinary_app_abi_contract.md'
CONTRACT_SHA = '541710f0e84b732b65890b451e43d8bc5ab34977367749b383ab3ae75ee48b2f'
ORIGINALS = {'state/analysis/P7_app_motor_fault_compile_raw/inspect_static_abi.py': (16600, '0eec2ffd91958831ab0541477a5277187bb7e9179fdca1096276dda01efb6f4c'), 'state/analysis/P7_motor_const_compile_raw/inspect_static_abi.py': (16087, 'f360a52d6e8c29227b8a59481f37f5e8a30b207d7b66fbffaa8e8785a4dedf3c'), 'state/analysis/P7_ordinary_app_static_compile_raw/inputs_static.json': (12940, 'a5e8f8b4b78312245c7cde3e86a39db9073b5ef9e5fa2806a3d39eece8600bb7'), 'state/analysis/P7_ordinary_app_static_compile_raw/native_static01/artifacts.json': (9281, '275ebb61be4a0487fe381d915ec28eea4634926b1d06a627850266f5c0a750e0'), 'state/analysis/P7_ordinary_app_static_compile_raw/native_static01/result.json': (1565, '221d02be2de722a8886a142328d3accb147cf1ab89b60ed9857e62fdd303aeb0'), 'tools/compile_ordinary_app_static.py': (26136, '40b5c765c01bc1749f6ea4534a4b7f274b681b5fa9295ab6f0c57fbf94d66a89')}
INPUT = (16600, '0eec2ffd91958831ab0541477a5277187bb7e9179fdca1096276dda01efb6f4c')
INTERMEDIATE = (16613, 'c6d2fad323649a0cc2d394925750df72d0040409abe020ae9c92faa2c81d0217')
PROJECTED = (12965, '7fb42d51a3f42f99c7e7890b4f4c1dc90360c2d84c09d3bbde7ccea4d1138aea')
METADATA_STEPS = ((b'state/analysis/P7_app_motor_fault_compile_raw', b'state/analysis/P7_ordinary_app_static_compile_raw', 1), (b'tools/compile_app_motor_fault.py', b'tools/compile_ordinary_app_static.py', 1), (b'app-motor-fault-static01', b'ordinary-app-static01', 1), (b'app-motor-fault-abi-static01', b'ordinary-app-abi-static01', 1), (b'D188_STATIC_FILE_ONLY_ABI', b'D209_STATIC_FILE_ONLY_ABI', 2), (b'21df6ae82cca4b09dc6b1e0de5bc719cf98ec6887800d5ce8297522e491a7950', b'9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a', 1), (b'cf0c826feca483a78ce9839d0037d1e005a0ce73a3aa01df1ad4b309729ed25a', b'40b5c765c01bc1749f6ea4534a4b7f274b681b5fa9295ab6f0c57fbf94d66a89', 1), (b'd4eae97c1c47a1ce0fa24c9d7e3ae44857a565cd7b85b9c17be45143654d3eb5', b'a5e8f8b4b78312245c7cde3e86a39db9073b5ef9e5fa2806a3d39eece8600bb7', 1), (b'f8928bd0b9a59f47c1bc02c627523af8f250535ffcd269e37e5a80414cc0ce82', b'221d02be2de722a8886a142328d3accb147cf1ab89b60ed9857e62fdd303aeb0', 1), (b'57b98c00db1ed5d90394812fcbb3fb28effedd4381f6e2fc03a6e7c04b45a6ce', b'275ebb61be4a0487fe381d915ec28eea4634926b1d06a627850266f5c0a750e0', 1), (b'self.compiler = loaded(COMPILE, HARD_PINS[COMPILE])', b'self.compiler = loaded(COMPILE, HARD_PINS[COMPILE]).load_caller(root=ROOT)', 1), (b'/build/app_motor_fault.ino', b'/build/app.ino', 1))
SEMANTIC_STEPS = (('TYPES', b"TYPES = ('app_motor_fault::Runner', 'app_motor_fault::Report', 'app_motor_fault::Snapshot',\n         'motor_fault::Trace', 'motor_fault::TraceReport', 'motor_fault::Call',\n         'app::Runtime', 'app::RuntimeReport', 'app::Transaction', 'app::TransactionReport',\n         'fsm::RobotResult', 'fsm::PreviousTick', 'motors::MotorGate', 'motors::Result',\n         'motors::HaltResult', 'core::Outputs', 'countdown::LifecycleResult', 'countdown::Result')\n", b"TYPES = ('app::Runtime', 'app::RuntimeReport', 'app::Transaction', 'app::TransactionReport', 'motors::MotorGate', 'motors::UnoQPort', 'motors::Result', 'motors::HaltResult', 'fsm::RobotResult', 'fsm::PreviousTick', 'core::Outputs', 'app::SetupGrants')\n"), ('WINDOWS', b"WINDOWS = {\n    'trace_.report_': 'motor_fault::TraceReport',\n    'report_': 'app_motor_fault::Report',\n    'report_.before_abort.runtime': 'app::RuntimeReport',\n    'report_.before_abort.transaction': 'app::TransactionReport',\n    'report_.before_abort.previous': 'fsm::PreviousTick',\n    'runtime_.report_': 'app::RuntimeReport',\n    'runtime_.transaction_.report_': 'app::TransactionReport',\n    'runtime_.transaction_.previous_': 'fsm::PreviousTick',\n    'runtime_.transaction_.gate_': 'motors::MotorGate',\n    'attempted_': 'bool',\n}\n", b"WINDOWS = {'report_': 'app::RuntimeReport', 'transaction_.report_': 'app::TransactionReport', 'transaction_.previous_': 'fsm::PreviousTick', 'transaction_.gate_': 'motors::MotorGate', 'grants_': 'app::SetupGrants', 'attempted_': 'bool'}\n"), ('queries', b"def queries(reader):\n    expressions = ['set max-value-size 1048576']\n    for name in (*TYPES, 'bool'):\n        for label, expression in (('SIZE', 'sizeof'), ('ALIGN', 'alignof')):\n            expressions += ['echo SUMOX_' + label + ' ' + name + '\\\\n',\n                            'p/d ' + expression + '(' + name + ')']\n        expressions += ['echo SUMOX_LAYOUT ' + name + '\\\\n', 'ptype /o ' + name]\n    for member in WINDOWS:\n        expressions += ['echo SUMOX_OFFSET ' + member + '\\\\n',\n                        'p/d (unsigned long)&((app_motor_fault::Runner*)0)->' + member]\n    build = OWNER + '/build/app.ino'\n    return [[reader.PREFIX + 'readelf', '--version'], [reader.PREFIX + 'gdb', '--version'],\n            [reader.PREFIX + 'readelf', '-hSWs', build + '.elf'],\n            reader.gdb(build + '_debug.elf', expressions)]\n", b'def queries(reader):\n    return _ordinary_queries(reader)\n'), ('summarize', b"def summarize(result, layout):\n    texts = [base64.b64decode(row['stdout_base64'], validate=True).decode('utf-8')\n             for row in result['commands']]\n    elf, debug = texts[2:]\n    require(re.search(r'^\\s*Type:\\s+EXEC \\(Executable file\\)\\s*$', elf, re.MULTILINE),\n            'Expected static ET_EXEC image')\n    sizes, aligns = {}, {}\n    for name in (*TYPES, 'bool'):\n        sizes[name], aligns[name] = number(debug, 'SIZE', name), number(debug, 'ALIGN', name)\n        require(0 < sizes[name] <= 1048576 and 0 < aligns[name] <= 16 and\n                aligns[name] & (aligns[name] - 1) == 0, 'Invalid ABI size/alignment')\n        require(debug.count('SUMOX_LAYOUT ' + name + '\\n') == 1, 'Missing layout marker')\n    symbol = '_ZN12_GLOBAL__N_110diagnosticE'\n    pattern = r'^\\s*\\d+:\\s+([0-9a-fA-F]+)\\s+(\\d+)\\s+OBJECT\\s+LOCAL\\s+DEFAULT\\s+(\\d+)\\s+' + symbol + r'\\s*$'\n    symbols = re.findall(pattern, elf, re.MULTILINE)\n    require(len(symbols) == 1, 'Expected exactly one static diagnostic OBJECT')\n    address, length, section = int(symbols[0][0], 16), int(symbols[0][1]), int(symbols[0][2])\n    bss = next(item for item in layout['sections'] if item['name'] == '.bss')\n    pattern = r'^\\s*\\[\\s*' + str(section) + r'\\]\\s+\\.bss\\s+NOBITS\\s+([0-9a-fA-F]+)\\s+[0-9a-fA-F]+\\s+([0-9a-fA-F]+)\\s+\\S+\\s+WA\\s+'\n    sections = re.findall(pattern, elf, re.MULTILINE)\n    require(len(sections) == 1 and tuple(int(x, 16) for x in sections[0]) ==\n            (bss['address'], bss['size']), 'Diagnostic section differs from checked layout')\n    require(length == sizes['app_motor_fault::Runner'] and address % aligns['app_motor_fault::Runner'] == 0 and\n            layout['bss_zero']['start'] <= address < address + length <= layout['bss_zero']['end'],\n            'Diagnostic object not wholly inside initialized BSS')\n    windows = {}\n    for member, name in WINDOWS.items():\n        offset = number(debug, 'OFFSET', member)\n        require(offset + sizes[name] <= length and (address + offset) % aligns[name] == 0,\n                'Capture window leaves diagnostic object or violates alignment')\n        windows[member] = dict(type=name, offset=offset, address=address + offset, bytes=sizes[name])\n    return dict(status='STATIC_ABI_OBSERVED', symbol=symbol, address=address, bytes=length,\n                section=section, sizes=sizes, alignments=aligns, windows=windows,\n                limitation='File layout only; no MCU contents, runtime acceptance, RAM or WCET measurement')\n", b'def summarize(result, layout):\n    return _ordinary_summary(result, layout, checked_command=checked_command)\n'))
ABI_TYPES = ('app::Runtime', 'app::RuntimeReport', 'app::Transaction', 'app::TransactionReport', 'motors::MotorGate', 'motors::UnoQPort', 'motors::Result', 'motors::HaltResult', 'fsm::RobotResult', 'fsm::PreviousTick', 'core::Outputs', 'app::SetupGrants', 'bool')
ABI_WINDOWS = {'report_': 'app::RuntimeReport', 'transaction_.report_': 'app::TransactionReport', 'transaction_.previous_': 'fsm::PreviousTick', 'transaction_.gate_': 'motors::MotorGate', 'grants_': 'app::SetupGrants', 'attempted_': 'bool'}
ENUMS = {'app::RuntimePhase': {'NOT_STARTED': 0, 'RUNNING': 1, 'STOPPED': 2, 'FAULT': 3, 'STOP_OBSERVING': 4}, 'app::RuntimeFault': {'NONE': 0, 'PORT': 1, 'CLOCK': 2, 'SERVICE_LIMIT': 3, 'TRANSACTION': 4, 'PROJECTION': 5}, 'app::Phase': {'NOT_INITIALIZED': 0, 'IDLE': 1, 'ACQUIRING': 2, 'DECIDED': 3, 'FAULT': 4}, 'app::Fault': {'NONE': 0, 'SETUP': 1, 'ORDER': 2, 'CLOCK': 3, 'IDENTITY': 4, 'RECEIPT': 5, 'ABORTED': 6}, 'motors::Fault': {'NONE': 0, 'NOT_INITIALIZED': 1, 'PORT': 2, 'IO': 3, 'COMMAND': 4, 'TOKEN': 5, 'STOPPED': 6}, 'core::State': {'BOOT': 0, 'IDLE': 1, 'COUNTDOWN': 2, 'OPENER': 3, 'SEARCH': 4, 'TRACK': 5, 'ATTACK': 6, 'DEFEND_TURN': 7, 'EDGE_ESCAPE': 8, 'REFLANK': 9, 'STOPPED': 10, 'DRIVE_TEST': 11}, 'edge::EscapeFault': {'NONE': 0, 'WHITE_PATTERN': 1, 'REPLAN_LIMIT': 2, 'PERMISSION_LOST': 3, 'INVALID_CONTEXT': 4}}
OBJECTS = (('runtime', '_ZN12_GLOBAL__N_17runtimeE', 'app::Runtime'), ('motor_port', '_ZN12_GLOBAL__N_110motor_portE', 'motors::UnoQPort'))
FORBIDDEN = ('_ZN12_GLOBAL__N_110diagnosticE', '_ZN6motors12_GLOBAL__N_119settle_probe_reportE', '_ZN6motors17settleProbeReportEv')
EXPRESSIONS = ('set max-value-size 1048576', 'echo SUMOX_SIZE app::Runtime\\n', 'p/d sizeof(app::Runtime)', 'echo SUMOX_ALIGN app::Runtime\\n', 'p/d alignof(app::Runtime)', 'echo SUMOX_LAYOUT app::Runtime\\n', 'ptype /o app::Runtime', 'echo SUMOX_SIZE app::RuntimeReport\\n', 'p/d sizeof(app::RuntimeReport)', 'echo SUMOX_ALIGN app::RuntimeReport\\n', 'p/d alignof(app::RuntimeReport)', 'echo SUMOX_LAYOUT app::RuntimeReport\\n', 'ptype /o app::RuntimeReport', 'echo SUMOX_SIZE app::Transaction\\n', 'p/d sizeof(app::Transaction)', 'echo SUMOX_ALIGN app::Transaction\\n', 'p/d alignof(app::Transaction)', 'echo SUMOX_LAYOUT app::Transaction\\n', 'ptype /o app::Transaction', 'echo SUMOX_SIZE app::TransactionReport\\n', 'p/d sizeof(app::TransactionReport)', 'echo SUMOX_ALIGN app::TransactionReport\\n', 'p/d alignof(app::TransactionReport)', 'echo SUMOX_LAYOUT app::TransactionReport\\n', 'ptype /o app::TransactionReport', 'echo SUMOX_SIZE motors::MotorGate\\n', 'p/d sizeof(motors::MotorGate)', 'echo SUMOX_ALIGN motors::MotorGate\\n', 'p/d alignof(motors::MotorGate)', 'echo SUMOX_LAYOUT motors::MotorGate\\n', 'ptype /o motors::MotorGate', 'echo SUMOX_SIZE motors::UnoQPort\\n', 'p/d sizeof(motors::UnoQPort)', 'echo SUMOX_ALIGN motors::UnoQPort\\n', 'p/d alignof(motors::UnoQPort)', 'echo SUMOX_LAYOUT motors::UnoQPort\\n', 'ptype /o motors::UnoQPort', 'echo SUMOX_SIZE motors::Result\\n', 'p/d sizeof(motors::Result)', 'echo SUMOX_ALIGN motors::Result\\n', 'p/d alignof(motors::Result)', 'echo SUMOX_LAYOUT motors::Result\\n', 'ptype /o motors::Result', 'echo SUMOX_SIZE motors::HaltResult\\n', 'p/d sizeof(motors::HaltResult)', 'echo SUMOX_ALIGN motors::HaltResult\\n', 'p/d alignof(motors::HaltResult)', 'echo SUMOX_LAYOUT motors::HaltResult\\n', 'ptype /o motors::HaltResult', 'echo SUMOX_SIZE fsm::RobotResult\\n', 'p/d sizeof(fsm::RobotResult)', 'echo SUMOX_ALIGN fsm::RobotResult\\n', 'p/d alignof(fsm::RobotResult)', 'echo SUMOX_LAYOUT fsm::RobotResult\\n', 'ptype /o fsm::RobotResult', 'echo SUMOX_SIZE fsm::PreviousTick\\n', 'p/d sizeof(fsm::PreviousTick)', 'echo SUMOX_ALIGN fsm::PreviousTick\\n', 'p/d alignof(fsm::PreviousTick)', 'echo SUMOX_LAYOUT fsm::PreviousTick\\n', 'ptype /o fsm::PreviousTick', 'echo SUMOX_SIZE core::Outputs\\n', 'p/d sizeof(core::Outputs)', 'echo SUMOX_ALIGN core::Outputs\\n', 'p/d alignof(core::Outputs)', 'echo SUMOX_LAYOUT core::Outputs\\n', 'ptype /o core::Outputs', 'echo SUMOX_SIZE app::SetupGrants\\n', 'p/d sizeof(app::SetupGrants)', 'echo SUMOX_ALIGN app::SetupGrants\\n', 'p/d alignof(app::SetupGrants)', 'echo SUMOX_LAYOUT app::SetupGrants\\n', 'ptype /o app::SetupGrants', 'echo SUMOX_SIZE bool\\n', 'p/d sizeof(bool)', 'echo SUMOX_ALIGN bool\\n', 'p/d alignof(bool)', 'echo SUMOX_LAYOUT bool\\n', 'ptype /o bool', 'echo SUMOX_OFFSET report_\\n', 'p/d (unsigned long)&((app::Runtime*)0)->report_', 'echo SUMOX_OFFSET transaction_.report_\\n', 'p/d (unsigned long)&((app::Runtime*)0)->transaction_.report_', 'echo SUMOX_OFFSET transaction_.previous_\\n', 'p/d (unsigned long)&((app::Runtime*)0)->transaction_.previous_', 'echo SUMOX_OFFSET transaction_.gate_\\n', 'p/d (unsigned long)&((app::Runtime*)0)->transaction_.gate_', 'echo SUMOX_OFFSET grants_\\n', 'p/d (unsigned long)&((app::Runtime*)0)->grants_', 'echo SUMOX_OFFSET attempted_\\n', 'p/d (unsigned long)&((app::Runtime*)0)->attempted_', 'echo SUMOX_ENUM app::RuntimePhase::NOT_STARTED\\n', 'p/d (unsigned int)app::RuntimePhase::NOT_STARTED', 'echo SUMOX_ENUM app::RuntimePhase::RUNNING\\n', 'p/d (unsigned int)app::RuntimePhase::RUNNING', 'echo SUMOX_ENUM app::RuntimePhase::STOPPED\\n', 'p/d (unsigned int)app::RuntimePhase::STOPPED', 'echo SUMOX_ENUM app::RuntimePhase::FAULT\\n', 'p/d (unsigned int)app::RuntimePhase::FAULT', 'echo SUMOX_ENUM app::RuntimePhase::STOP_OBSERVING\\n', 'p/d (unsigned int)app::RuntimePhase::STOP_OBSERVING', 'echo SUMOX_ENUM app::RuntimeFault::NONE\\n', 'p/d (unsigned int)app::RuntimeFault::NONE', 'echo SUMOX_ENUM app::RuntimeFault::PORT\\n', 'p/d (unsigned int)app::RuntimeFault::PORT', 'echo SUMOX_ENUM app::RuntimeFault::CLOCK\\n', 'p/d (unsigned int)app::RuntimeFault::CLOCK', 'echo SUMOX_ENUM app::RuntimeFault::SERVICE_LIMIT\\n', 'p/d (unsigned int)app::RuntimeFault::SERVICE_LIMIT', 'echo SUMOX_ENUM app::RuntimeFault::TRANSACTION\\n', 'p/d (unsigned int)app::RuntimeFault::TRANSACTION', 'echo SUMOX_ENUM app::RuntimeFault::PROJECTION\\n', 'p/d (unsigned int)app::RuntimeFault::PROJECTION', 'echo SUMOX_ENUM app::Phase::NOT_INITIALIZED\\n', 'p/d (unsigned int)app::Phase::NOT_INITIALIZED', 'echo SUMOX_ENUM app::Phase::IDLE\\n', 'p/d (unsigned int)app::Phase::IDLE', 'echo SUMOX_ENUM app::Phase::ACQUIRING\\n', 'p/d (unsigned int)app::Phase::ACQUIRING', 'echo SUMOX_ENUM app::Phase::DECIDED\\n', 'p/d (unsigned int)app::Phase::DECIDED', 'echo SUMOX_ENUM app::Phase::FAULT\\n', 'p/d (unsigned int)app::Phase::FAULT', 'echo SUMOX_ENUM app::Fault::NONE\\n', 'p/d (unsigned int)app::Fault::NONE', 'echo SUMOX_ENUM app::Fault::SETUP\\n', 'p/d (unsigned int)app::Fault::SETUP', 'echo SUMOX_ENUM app::Fault::ORDER\\n', 'p/d (unsigned int)app::Fault::ORDER', 'echo SUMOX_ENUM app::Fault::CLOCK\\n', 'p/d (unsigned int)app::Fault::CLOCK', 'echo SUMOX_ENUM app::Fault::IDENTITY\\n', 'p/d (unsigned int)app::Fault::IDENTITY', 'echo SUMOX_ENUM app::Fault::RECEIPT\\n', 'p/d (unsigned int)app::Fault::RECEIPT', 'echo SUMOX_ENUM app::Fault::ABORTED\\n', 'p/d (unsigned int)app::Fault::ABORTED', 'echo SUMOX_ENUM motors::Fault::NONE\\n', 'p/d (unsigned int)motors::Fault::NONE', 'echo SUMOX_ENUM motors::Fault::NOT_INITIALIZED\\n', 'p/d (unsigned int)motors::Fault::NOT_INITIALIZED', 'echo SUMOX_ENUM motors::Fault::PORT\\n', 'p/d (unsigned int)motors::Fault::PORT', 'echo SUMOX_ENUM motors::Fault::IO\\n', 'p/d (unsigned int)motors::Fault::IO', 'echo SUMOX_ENUM motors::Fault::COMMAND\\n', 'p/d (unsigned int)motors::Fault::COMMAND', 'echo SUMOX_ENUM motors::Fault::TOKEN\\n', 'p/d (unsigned int)motors::Fault::TOKEN', 'echo SUMOX_ENUM motors::Fault::STOPPED\\n', 'p/d (unsigned int)motors::Fault::STOPPED', 'echo SUMOX_ENUM core::State::BOOT\\n', 'p/d (unsigned int)core::State::BOOT', 'echo SUMOX_ENUM core::State::IDLE\\n', 'p/d (unsigned int)core::State::IDLE', 'echo SUMOX_ENUM core::State::COUNTDOWN\\n', 'p/d (unsigned int)core::State::COUNTDOWN', 'echo SUMOX_ENUM core::State::OPENER\\n', 'p/d (unsigned int)core::State::OPENER', 'echo SUMOX_ENUM core::State::SEARCH\\n', 'p/d (unsigned int)core::State::SEARCH', 'echo SUMOX_ENUM core::State::TRACK\\n', 'p/d (unsigned int)core::State::TRACK', 'echo SUMOX_ENUM core::State::ATTACK\\n', 'p/d (unsigned int)core::State::ATTACK', 'echo SUMOX_ENUM core::State::DEFEND_TURN\\n', 'p/d (unsigned int)core::State::DEFEND_TURN', 'echo SUMOX_ENUM core::State::EDGE_ESCAPE\\n', 'p/d (unsigned int)core::State::EDGE_ESCAPE', 'echo SUMOX_ENUM core::State::REFLANK\\n', 'p/d (unsigned int)core::State::REFLANK', 'echo SUMOX_ENUM core::State::STOPPED\\n', 'p/d (unsigned int)core::State::STOPPED', 'echo SUMOX_ENUM core::State::DRIVE_TEST\\n', 'p/d (unsigned int)core::State::DRIVE_TEST', 'echo SUMOX_ENUM edge::EscapeFault::NONE\\n', 'p/d (unsigned int)edge::EscapeFault::NONE', 'echo SUMOX_ENUM edge::EscapeFault::WHITE_PATTERN\\n', 'p/d (unsigned int)edge::EscapeFault::WHITE_PATTERN', 'echo SUMOX_ENUM edge::EscapeFault::REPLAN_LIMIT\\n', 'p/d (unsigned int)edge::EscapeFault::REPLAN_LIMIT', 'echo SUMOX_ENUM edge::EscapeFault::PERMISSION_LOST\\n', 'p/d (unsigned int)edge::EscapeFault::PERMISSION_LOST', 'echo SUMOX_ENUM edge::EscapeFault::INVALID_CONTEXT\\n', 'p/d (unsigned int)edge::EscapeFault::INVALID_CONTEXT')
MARKERS = ('SUMOX_SIZE app::Runtime', 'SUMOX_ALIGN app::Runtime', 'SUMOX_LAYOUT app::Runtime', 'SUMOX_SIZE app::RuntimeReport', 'SUMOX_ALIGN app::RuntimeReport', 'SUMOX_LAYOUT app::RuntimeReport', 'SUMOX_SIZE app::Transaction', 'SUMOX_ALIGN app::Transaction', 'SUMOX_LAYOUT app::Transaction', 'SUMOX_SIZE app::TransactionReport', 'SUMOX_ALIGN app::TransactionReport', 'SUMOX_LAYOUT app::TransactionReport', 'SUMOX_SIZE motors::MotorGate', 'SUMOX_ALIGN motors::MotorGate', 'SUMOX_LAYOUT motors::MotorGate', 'SUMOX_SIZE motors::UnoQPort', 'SUMOX_ALIGN motors::UnoQPort', 'SUMOX_LAYOUT motors::UnoQPort', 'SUMOX_SIZE motors::Result', 'SUMOX_ALIGN motors::Result', 'SUMOX_LAYOUT motors::Result', 'SUMOX_SIZE motors::HaltResult', 'SUMOX_ALIGN motors::HaltResult', 'SUMOX_LAYOUT motors::HaltResult', 'SUMOX_SIZE fsm::RobotResult', 'SUMOX_ALIGN fsm::RobotResult', 'SUMOX_LAYOUT fsm::RobotResult', 'SUMOX_SIZE fsm::PreviousTick', 'SUMOX_ALIGN fsm::PreviousTick', 'SUMOX_LAYOUT fsm::PreviousTick', 'SUMOX_SIZE core::Outputs', 'SUMOX_ALIGN core::Outputs', 'SUMOX_LAYOUT core::Outputs', 'SUMOX_SIZE app::SetupGrants', 'SUMOX_ALIGN app::SetupGrants', 'SUMOX_LAYOUT app::SetupGrants', 'SUMOX_SIZE bool', 'SUMOX_ALIGN bool', 'SUMOX_LAYOUT bool', 'SUMOX_OFFSET report_', 'SUMOX_OFFSET transaction_.report_', 'SUMOX_OFFSET transaction_.previous_', 'SUMOX_OFFSET transaction_.gate_', 'SUMOX_OFFSET grants_', 'SUMOX_OFFSET attempted_', 'SUMOX_ENUM app::RuntimePhase::NOT_STARTED', 'SUMOX_ENUM app::RuntimePhase::RUNNING', 'SUMOX_ENUM app::RuntimePhase::STOPPED', 'SUMOX_ENUM app::RuntimePhase::FAULT', 'SUMOX_ENUM app::RuntimePhase::STOP_OBSERVING', 'SUMOX_ENUM app::RuntimeFault::NONE', 'SUMOX_ENUM app::RuntimeFault::PORT', 'SUMOX_ENUM app::RuntimeFault::CLOCK', 'SUMOX_ENUM app::RuntimeFault::SERVICE_LIMIT', 'SUMOX_ENUM app::RuntimeFault::TRANSACTION', 'SUMOX_ENUM app::RuntimeFault::PROJECTION', 'SUMOX_ENUM app::Phase::NOT_INITIALIZED', 'SUMOX_ENUM app::Phase::IDLE', 'SUMOX_ENUM app::Phase::ACQUIRING', 'SUMOX_ENUM app::Phase::DECIDED', 'SUMOX_ENUM app::Phase::FAULT', 'SUMOX_ENUM app::Fault::NONE', 'SUMOX_ENUM app::Fault::SETUP', 'SUMOX_ENUM app::Fault::ORDER', 'SUMOX_ENUM app::Fault::CLOCK', 'SUMOX_ENUM app::Fault::IDENTITY', 'SUMOX_ENUM app::Fault::RECEIPT', 'SUMOX_ENUM app::Fault::ABORTED', 'SUMOX_ENUM motors::Fault::NONE', 'SUMOX_ENUM motors::Fault::NOT_INITIALIZED', 'SUMOX_ENUM motors::Fault::PORT', 'SUMOX_ENUM motors::Fault::IO', 'SUMOX_ENUM motors::Fault::COMMAND', 'SUMOX_ENUM motors::Fault::TOKEN', 'SUMOX_ENUM motors::Fault::STOPPED', 'SUMOX_ENUM core::State::BOOT', 'SUMOX_ENUM core::State::IDLE', 'SUMOX_ENUM core::State::COUNTDOWN', 'SUMOX_ENUM core::State::OPENER', 'SUMOX_ENUM core::State::SEARCH', 'SUMOX_ENUM core::State::TRACK', 'SUMOX_ENUM core::State::ATTACK', 'SUMOX_ENUM core::State::DEFEND_TURN', 'SUMOX_ENUM core::State::EDGE_ESCAPE', 'SUMOX_ENUM core::State::REFLANK', 'SUMOX_ENUM core::State::STOPPED', 'SUMOX_ENUM core::State::DRIVE_TEST', 'SUMOX_ENUM edge::EscapeFault::NONE', 'SUMOX_ENUM edge::EscapeFault::WHITE_PATTERN', 'SUMOX_ENUM edge::EscapeFault::REPLAN_LIMIT', 'SUMOX_ENUM edge::EscapeFault::PERMISSION_LOST', 'SUMOX_ENUM edge::EscapeFault::INVALID_CONTEXT')
COMMANDS = (('/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin/arm-zephyr-eabi-readelf', '--version'), ('/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin/arm-zephyr-eabi-gdb', '--version'), ('/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin/arm-zephyr-eabi-readelf', '-hSWs', '/home/arduino/sumox26_codex_build/ordinary-app-static01/build/app.ino.elf'), ('/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin/arm-zephyr-eabi-gdb', '-nx', '-nh', '-batch', '-iex', 'set auto-load no', '/home/arduino/sumox26_codex_build/ordinary-app-static01/build/app.ino_debug.elf', '-ex', 'set language c++', '-ex', 'set may-call-functions off', '-ex', 'set max-value-size 1048576', '-ex', 'echo SUMOX_SIZE app::Runtime\\n', '-ex', 'p/d sizeof(app::Runtime)', '-ex', 'echo SUMOX_ALIGN app::Runtime\\n', '-ex', 'p/d alignof(app::Runtime)', '-ex', 'echo SUMOX_LAYOUT app::Runtime\\n', '-ex', 'ptype /o app::Runtime', '-ex', 'echo SUMOX_SIZE app::RuntimeReport\\n', '-ex', 'p/d sizeof(app::RuntimeReport)', '-ex', 'echo SUMOX_ALIGN app::RuntimeReport\\n', '-ex', 'p/d alignof(app::RuntimeReport)', '-ex', 'echo SUMOX_LAYOUT app::RuntimeReport\\n', '-ex', 'ptype /o app::RuntimeReport', '-ex', 'echo SUMOX_SIZE app::Transaction\\n', '-ex', 'p/d sizeof(app::Transaction)', '-ex', 'echo SUMOX_ALIGN app::Transaction\\n', '-ex', 'p/d alignof(app::Transaction)', '-ex', 'echo SUMOX_LAYOUT app::Transaction\\n', '-ex', 'ptype /o app::Transaction', '-ex', 'echo SUMOX_SIZE app::TransactionReport\\n', '-ex', 'p/d sizeof(app::TransactionReport)', '-ex', 'echo SUMOX_ALIGN app::TransactionReport\\n', '-ex', 'p/d alignof(app::TransactionReport)', '-ex', 'echo SUMOX_LAYOUT app::TransactionReport\\n', '-ex', 'ptype /o app::TransactionReport', '-ex', 'echo SUMOX_SIZE motors::MotorGate\\n', '-ex', 'p/d sizeof(motors::MotorGate)', '-ex', 'echo SUMOX_ALIGN motors::MotorGate\\n', '-ex', 'p/d alignof(motors::MotorGate)', '-ex', 'echo SUMOX_LAYOUT motors::MotorGate\\n', '-ex', 'ptype /o motors::MotorGate', '-ex', 'echo SUMOX_SIZE motors::UnoQPort\\n', '-ex', 'p/d sizeof(motors::UnoQPort)', '-ex', 'echo SUMOX_ALIGN motors::UnoQPort\\n', '-ex', 'p/d alignof(motors::UnoQPort)', '-ex', 'echo SUMOX_LAYOUT motors::UnoQPort\\n', '-ex', 'ptype /o motors::UnoQPort', '-ex', 'echo SUMOX_SIZE motors::Result\\n', '-ex', 'p/d sizeof(motors::Result)', '-ex', 'echo SUMOX_ALIGN motors::Result\\n', '-ex', 'p/d alignof(motors::Result)', '-ex', 'echo SUMOX_LAYOUT motors::Result\\n', '-ex', 'ptype /o motors::Result', '-ex', 'echo SUMOX_SIZE motors::HaltResult\\n', '-ex', 'p/d sizeof(motors::HaltResult)', '-ex', 'echo SUMOX_ALIGN motors::HaltResult\\n', '-ex', 'p/d alignof(motors::HaltResult)', '-ex', 'echo SUMOX_LAYOUT motors::HaltResult\\n', '-ex', 'ptype /o motors::HaltResult', '-ex', 'echo SUMOX_SIZE fsm::RobotResult\\n', '-ex', 'p/d sizeof(fsm::RobotResult)', '-ex', 'echo SUMOX_ALIGN fsm::RobotResult\\n', '-ex', 'p/d alignof(fsm::RobotResult)', '-ex', 'echo SUMOX_LAYOUT fsm::RobotResult\\n', '-ex', 'ptype /o fsm::RobotResult', '-ex', 'echo SUMOX_SIZE fsm::PreviousTick\\n', '-ex', 'p/d sizeof(fsm::PreviousTick)', '-ex', 'echo SUMOX_ALIGN fsm::PreviousTick\\n', '-ex', 'p/d alignof(fsm::PreviousTick)', '-ex', 'echo SUMOX_LAYOUT fsm::PreviousTick\\n', '-ex', 'ptype /o fsm::PreviousTick', '-ex', 'echo SUMOX_SIZE core::Outputs\\n', '-ex', 'p/d sizeof(core::Outputs)', '-ex', 'echo SUMOX_ALIGN core::Outputs\\n', '-ex', 'p/d alignof(core::Outputs)', '-ex', 'echo SUMOX_LAYOUT core::Outputs\\n', '-ex', 'ptype /o core::Outputs', '-ex', 'echo SUMOX_SIZE app::SetupGrants\\n', '-ex', 'p/d sizeof(app::SetupGrants)', '-ex', 'echo SUMOX_ALIGN app::SetupGrants\\n', '-ex', 'p/d alignof(app::SetupGrants)', '-ex', 'echo SUMOX_LAYOUT app::SetupGrants\\n', '-ex', 'ptype /o app::SetupGrants', '-ex', 'echo SUMOX_SIZE bool\\n', '-ex', 'p/d sizeof(bool)', '-ex', 'echo SUMOX_ALIGN bool\\n', '-ex', 'p/d alignof(bool)', '-ex', 'echo SUMOX_LAYOUT bool\\n', '-ex', 'ptype /o bool', '-ex', 'echo SUMOX_OFFSET report_\\n', '-ex', 'p/d (unsigned long)&((app::Runtime*)0)->report_', '-ex', 'echo SUMOX_OFFSET transaction_.report_\\n', '-ex', 'p/d (unsigned long)&((app::Runtime*)0)->transaction_.report_', '-ex', 'echo SUMOX_OFFSET transaction_.previous_\\n', '-ex', 'p/d (unsigned long)&((app::Runtime*)0)->transaction_.previous_', '-ex', 'echo SUMOX_OFFSET transaction_.gate_\\n', '-ex', 'p/d (unsigned long)&((app::Runtime*)0)->transaction_.gate_', '-ex', 'echo SUMOX_OFFSET grants_\\n', '-ex', 'p/d (unsigned long)&((app::Runtime*)0)->grants_', '-ex', 'echo SUMOX_OFFSET attempted_\\n', '-ex', 'p/d (unsigned long)&((app::Runtime*)0)->attempted_', '-ex', 'echo SUMOX_ENUM app::RuntimePhase::NOT_STARTED\\n', '-ex', 'p/d (unsigned int)app::RuntimePhase::NOT_STARTED', '-ex', 'echo SUMOX_ENUM app::RuntimePhase::RUNNING\\n', '-ex', 'p/d (unsigned int)app::RuntimePhase::RUNNING', '-ex', 'echo SUMOX_ENUM app::RuntimePhase::STOPPED\\n', '-ex', 'p/d (unsigned int)app::RuntimePhase::STOPPED', '-ex', 'echo SUMOX_ENUM app::RuntimePhase::FAULT\\n', '-ex', 'p/d (unsigned int)app::RuntimePhase::FAULT', '-ex', 'echo SUMOX_ENUM app::RuntimePhase::STOP_OBSERVING\\n', '-ex', 'p/d (unsigned int)app::RuntimePhase::STOP_OBSERVING', '-ex', 'echo SUMOX_ENUM app::RuntimeFault::NONE\\n', '-ex', 'p/d (unsigned int)app::RuntimeFault::NONE', '-ex', 'echo SUMOX_ENUM app::RuntimeFault::PORT\\n', '-ex', 'p/d (unsigned int)app::RuntimeFault::PORT', '-ex', 'echo SUMOX_ENUM app::RuntimeFault::CLOCK\\n', '-ex', 'p/d (unsigned int)app::RuntimeFault::CLOCK', '-ex', 'echo SUMOX_ENUM app::RuntimeFault::SERVICE_LIMIT\\n', '-ex', 'p/d (unsigned int)app::RuntimeFault::SERVICE_LIMIT', '-ex', 'echo SUMOX_ENUM app::RuntimeFault::TRANSACTION\\n', '-ex', 'p/d (unsigned int)app::RuntimeFault::TRANSACTION', '-ex', 'echo SUMOX_ENUM app::RuntimeFault::PROJECTION\\n', '-ex', 'p/d (unsigned int)app::RuntimeFault::PROJECTION', '-ex', 'echo SUMOX_ENUM app::Phase::NOT_INITIALIZED\\n', '-ex', 'p/d (unsigned int)app::Phase::NOT_INITIALIZED', '-ex', 'echo SUMOX_ENUM app::Phase::IDLE\\n', '-ex', 'p/d (unsigned int)app::Phase::IDLE', '-ex', 'echo SUMOX_ENUM app::Phase::ACQUIRING\\n', '-ex', 'p/d (unsigned int)app::Phase::ACQUIRING', '-ex', 'echo SUMOX_ENUM app::Phase::DECIDED\\n', '-ex', 'p/d (unsigned int)app::Phase::DECIDED', '-ex', 'echo SUMOX_ENUM app::Phase::FAULT\\n', '-ex', 'p/d (unsigned int)app::Phase::FAULT', '-ex', 'echo SUMOX_ENUM app::Fault::NONE\\n', '-ex', 'p/d (unsigned int)app::Fault::NONE', '-ex', 'echo SUMOX_ENUM app::Fault::SETUP\\n', '-ex', 'p/d (unsigned int)app::Fault::SETUP', '-ex', 'echo SUMOX_ENUM app::Fault::ORDER\\n', '-ex', 'p/d (unsigned int)app::Fault::ORDER', '-ex', 'echo SUMOX_ENUM app::Fault::CLOCK\\n', '-ex', 'p/d (unsigned int)app::Fault::CLOCK', '-ex', 'echo SUMOX_ENUM app::Fault::IDENTITY\\n', '-ex', 'p/d (unsigned int)app::Fault::IDENTITY', '-ex', 'echo SUMOX_ENUM app::Fault::RECEIPT\\n', '-ex', 'p/d (unsigned int)app::Fault::RECEIPT', '-ex', 'echo SUMOX_ENUM app::Fault::ABORTED\\n', '-ex', 'p/d (unsigned int)app::Fault::ABORTED', '-ex', 'echo SUMOX_ENUM motors::Fault::NONE\\n', '-ex', 'p/d (unsigned int)motors::Fault::NONE', '-ex', 'echo SUMOX_ENUM motors::Fault::NOT_INITIALIZED\\n', '-ex', 'p/d (unsigned int)motors::Fault::NOT_INITIALIZED', '-ex', 'echo SUMOX_ENUM motors::Fault::PORT\\n', '-ex', 'p/d (unsigned int)motors::Fault::PORT', '-ex', 'echo SUMOX_ENUM motors::Fault::IO\\n', '-ex', 'p/d (unsigned int)motors::Fault::IO', '-ex', 'echo SUMOX_ENUM motors::Fault::COMMAND\\n', '-ex', 'p/d (unsigned int)motors::Fault::COMMAND', '-ex', 'echo SUMOX_ENUM motors::Fault::TOKEN\\n', '-ex', 'p/d (unsigned int)motors::Fault::TOKEN', '-ex', 'echo SUMOX_ENUM motors::Fault::STOPPED\\n', '-ex', 'p/d (unsigned int)motors::Fault::STOPPED', '-ex', 'echo SUMOX_ENUM core::State::BOOT\\n', '-ex', 'p/d (unsigned int)core::State::BOOT', '-ex', 'echo SUMOX_ENUM core::State::IDLE\\n', '-ex', 'p/d (unsigned int)core::State::IDLE', '-ex', 'echo SUMOX_ENUM core::State::COUNTDOWN\\n', '-ex', 'p/d (unsigned int)core::State::COUNTDOWN', '-ex', 'echo SUMOX_ENUM core::State::OPENER\\n', '-ex', 'p/d (unsigned int)core::State::OPENER', '-ex', 'echo SUMOX_ENUM core::State::SEARCH\\n', '-ex', 'p/d (unsigned int)core::State::SEARCH', '-ex', 'echo SUMOX_ENUM core::State::TRACK\\n', '-ex', 'p/d (unsigned int)core::State::TRACK', '-ex', 'echo SUMOX_ENUM core::State::ATTACK\\n', '-ex', 'p/d (unsigned int)core::State::ATTACK', '-ex', 'echo SUMOX_ENUM core::State::DEFEND_TURN\\n', '-ex', 'p/d (unsigned int)core::State::DEFEND_TURN', '-ex', 'echo SUMOX_ENUM core::State::EDGE_ESCAPE\\n', '-ex', 'p/d (unsigned int)core::State::EDGE_ESCAPE', '-ex', 'echo SUMOX_ENUM core::State::REFLANK\\n', '-ex', 'p/d (unsigned int)core::State::REFLANK', '-ex', 'echo SUMOX_ENUM core::State::STOPPED\\n', '-ex', 'p/d (unsigned int)core::State::STOPPED', '-ex', 'echo SUMOX_ENUM core::State::DRIVE_TEST\\n', '-ex', 'p/d (unsigned int)core::State::DRIVE_TEST', '-ex', 'echo SUMOX_ENUM edge::EscapeFault::NONE\\n', '-ex', 'p/d (unsigned int)edge::EscapeFault::NONE', '-ex', 'echo SUMOX_ENUM edge::EscapeFault::WHITE_PATTERN\\n', '-ex', 'p/d (unsigned int)edge::EscapeFault::WHITE_PATTERN', '-ex', 'echo SUMOX_ENUM edge::EscapeFault::REPLAN_LIMIT\\n', '-ex', 'p/d (unsigned int)edge::EscapeFault::REPLAN_LIMIT', '-ex', 'echo SUMOX_ENUM edge::EscapeFault::PERMISSION_LOST\\n', '-ex', 'p/d (unsigned int)edge::EscapeFault::PERMISSION_LOST', '-ex', 'echo SUMOX_ENUM edge::EscapeFault::INVALID_CONTEXT\\n', '-ex', 'p/d (unsigned int)edge::EscapeFault::INVALID_CONTEXT'))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def _stamp(info):
    return (info.st_dev, info.st_ino, info.st_mode, info.st_nlink, info.st_size,
            info.st_mtime_ns, getattr(info, 'st_file_attributes', 0), info.st_ctime_ns)


def _plain_chain(path):
    stamps = []
    for item in (*reversed(path.parents), path):
        info = item.lstat()
        expected = stat.S_ISREG if item == path else stat.S_ISDIR
        require(expected(info.st_mode) and not getattr(info, 'st_file_attributes', 0) & 1024,
                'Nonplain ABI input path: ' + str(item))
        require(item != path or info.st_nlink == 1, 'ABI input has multiple links')
        stamps.append(_stamp(info))
    return stamps


def _read_handle(path, expected, limit, before):
    descriptor, stream, primary = None, None, None
    flags = os.O_RDONLY | getattr(os, 'O_BINARY', 0) | getattr(os, 'O_CLOEXEC', 0)
    flags |= getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0)
    try:
        descriptor = os.open(path, flags)
        info = os.fstat(descriptor)
        opened = _stamp(info)
        path_identity = before[-1][:-1] if os.name == 'nt' else before[-1]
        handle_identity = opened[:-1] if os.name == 'nt' else opened
        # CPython adds all execute bits to these Windows pathname stat results.
        if (os.name == 'nt' and path.suffix.lower() in ('.exe', '.bat', '.cmd', '.com') and
                stat.S_ISREG(path_identity[2]) and stat.S_ISREG(handle_identity[2]) and
                path_identity[2] == (handle_identity[2] | 0o111) and
                path_identity[2] ^ handle_identity[2] == 0o111):
            handle_identity = (*handle_identity[:2], path_identity[2], *handle_identity[3:])
        require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and
                not getattr(info, 'st_file_attributes', 0) & 1024 and
                path_identity == handle_identity, 'ABI input changed before reading')
        stream = os.fdopen(descriptor, 'rb')
        descriptor = None
        raw = stream.read(limit + 1)
        closed = _stamp(os.fstat(stream.fileno()))
        after = _plain_chain(path)
        require(before == after and opened == closed and
                0 < len(raw) == before[-1][4] <= limit, 'ABI input changed while reading')
        require(hashlib.sha256(raw).hexdigest() == expected, 'ABI input digest changed: ' + str(path))
        return raw
    except BaseException as error:
        primary = error
        raise
    finally:
        try:
            if stream is not None:
                stream.close()
            elif descriptor is not None:
                os.close(descriptor)
        except BaseException:
            if primary is None:
                raise


def pinned(path, expected, limit=1048576):
    require(type(expected) is str and re.fullmatch('[0-9a-f]{64}', expected),
            'Expected a fixed lowercase input digest')
    require(type(limit) is int and 0 < limit <= 16777216, 'Invalid ABI input bound')
    path = Path(path).absolute()
    before = _plain_chain(path)
    require(0 < before[-1][4] <= limit, 'ABI input exceeds byte bound')
    return _read_handle(path, expected, limit, before)


def _verify(raw, identity, label):
    require(type(raw) is bytes and len(raw) == identity[0] and
            hashlib.sha256(raw).hexdigest() == identity[1], 'Fixed source changed: ' + label)


def project_reader(raw):
    _verify(raw, INPUT, 'D188 reader')
    for old, new, count in METADATA_STEPS:
        require(raw.count(old) == count, 'ABI metadata occurrence changed')
        raw = raw.replace(old, new)
    _verify(raw, INTERMEDIATE, 'Ordinary metadata intermediate')
    for name, old, new in SEMANTIC_STEPS:
        require(raw.count(old) == 1, 'ABI semantic span changed: ' + name)
        raw = raw.replace(old, new)
    _verify(raw, PROJECTED, 'Ordinary projected reader')
    return raw


def _ordinary_queries(reader):
    build = '/home/arduino/sumox26_codex_build/ordinary-app-static01/build/app.ino'
    commands = [[reader.PREFIX + 'readelf', '--version'],
                [reader.PREFIX + 'gdb', '--version'],
                [reader.PREFIX + 'readelf', '-hSWs', build + '.elf'],
                reader.gdb(build + '_debug.elf', list(EXPRESSIONS))]
    require(commands == [list(c) for c in COMMANDS], 'Ordinary file commands changed')
    return commands


def _streams(result, checked_command):
    require(type(result) is dict and result.get('first_error') is None and
            result.get('status') == 'OBSERVED' and callable(checked_command),
            'Expected successful file-only result')
    records = result.get('commands')
    require(type(records) is list and len(records) == 4 and
            all(type(r) is dict for r in records), 'Expected four file commands')
    texts = []
    for record, command in zip(records, COMMANDS):
        checked_command(record, list(command))
        require(type(record.get('deadline_seconds')) is int and
                type(record.get('reap_seconds')) is int and
                type(record['execution'].get('returncode')) is int and
                type(record['execution'].get('timed_out')) is bool and
                type(record['execution'].get('reaped')) is bool,
                'Invalid file execution scalar types')
        texts.append(base64.b64decode(record['stdout_base64'], validate=True).decode('utf-8'))
    return texts[2], texts[3]


def _debug_blocks(text):
    lines = text.splitlines(keepends=True)
    positions = [i for i, line in enumerate(lines) if 'SUMOX_' in line]
    observed = [lines[i].rstrip('\r\n') for i in positions]
    require(observed == list(MARKERS), 'Ordinary ABI markers differ or are reordered')
    require(not ''.join(lines[:positions[0]]).strip(), 'Unexpected ABI debug prefix')
    blocks = {}
    for j, start in enumerate(positions):
        end = positions[j + 1] if j + 1 < len(positions) else len(lines)
        blocks[observed[j]] = ''.join(lines[start + 1:end])
    return blocks


def _numeric(blocks, label, name):
    value = blocks['SUMOX_' + label + ' ' + name].strip('\r\n')
    match = re.fullmatch(r'\$[0-9]+ = (0|[1-9][0-9]*)', value)
    require(match is not None, 'Missing or malformed ABI number: ' + label + ' ' + name)
    return int(match.group(1))


def _complete_layout(block, name):
    value = block.strip()
    require(bool(value), 'Empty ABI layout: ' + name)
    if name == 'bool':
        require(value == 'type = bool', 'Unsupported bool layout')
        return block
    pattern = r'^(?:/\*[^\n]*\*/\s*)?type = (?:class|struct) ' + re.escape(name) + r'\s*\{'
    require(re.search(pattern, value) is not None and value.endswith('}'),
            'Unsupported or incomplete ABI layout: ' + name)
    depth = 0
    for char in value:
        depth += (char == '{') - (char == '}')
        require(depth >= 0, 'Unbalanced ABI layout: ' + name)
    require(depth == 0, 'Incomplete ABI layout: ' + name)
    return block


def _type_observations(blocks):
    sizes, aligns, layouts = {}, {}, {}
    for name in ABI_TYPES:
        size, alignment = _numeric(blocks, 'SIZE', name), _numeric(blocks, 'ALIGN', name)
        require(0 < size <= 1048576 and 0 < alignment <= 16 and
                alignment & (alignment - 1) == 0, 'Invalid ordinary ABI size/alignment')
        sizes[name], aligns[name] = size, alignment
        layouts[name] = _complete_layout(blocks['SUMOX_LAYOUT ' + name], name)
    require(sizes['bool'] == aligns['bool'] == 1, 'Unsupported bool ABI')
    return sizes, aligns, layouts


def _bss(elf, layout):
    require(type(layout) is dict and type(layout.get('sections')) is list,
            'Missing checked ELF sections')
    candidates = [s for s in layout['sections'] if type(s) is dict and s.get('name') == '.bss']
    require(len(candidates) == 1, 'Expected one checked BSS section')
    bss, zero = candidates[0], layout.get('bss_zero')
    require(type(zero) is dict and all(type(bss.get(k)) is int for k in ('address', 'size')) and
            all(type(zero.get(k)) is int for k in ('start', 'end')) and
            0 <= bss['address'] <= zero['start'] < zero['end'] <= bss['address'] + bss['size'],
            'Invalid initialized BSS interval')
    rows = [line for line in elf.splitlines() if re.match(r'^\s*\[[^\]]*\]\s+\.bss(?:\s|$)', line)]
    require(len(rows) == 1, 'Missing or duplicate native BSS section')
    pattern = (r'\s*\[\s*([0-9]+)\]\s+\.bss\s+NOBITS\s+([0-9a-fA-F]+)\s+'
               r'[0-9a-fA-F]+\s+([0-9a-fA-F]+)\s+[0-9a-fA-F]+\s+WA\s+'
               r'[0-9]+\s+[0-9]+\s+[0-9]+\s*')
    match = re.fullmatch(pattern, rows[0])
    require(match is not None and (int(match[2], 16), int(match[3], 16)) ==
            (bss['address'], bss['size']), 'Native BSS differs from checked layout')
    return int(match[1]), zero


def _symbol(elf, symbol):
    token = r'(?<!\S)' + re.escape(symbol) + r'(?!\S)'
    rows = [line for line in elf.splitlines() if re.search(token, line)]
    require(len(rows) == 1, 'Missing or duplicate ordinary object: ' + symbol)
    pattern = (r'\s*[0-9]+:\s+([0-9a-fA-F]+)\s+(0x[0-9a-fA-F]+|[0-9]+)\s+'
               r'OBJECT\s+LOCAL\s+DEFAULT\s+([0-9]+)\s+' + re.escape(symbol) + r'\s*')
    match = re.fullmatch(pattern, rows[0])
    require(match is not None, 'Malformed ordinary object: ' + symbol)
    size = int(match[2], 16 if match[2].startswith('0x') else 10)
    return int(match[1], 16), size, int(match[3])


def _objects(elf, layout, sizes, aligns):
    kinds = re.findall(r'^\s*Type:\s*(.*?)\s*$', elf, re.MULTILINE)
    require(kinds == ['EXEC (Executable file)'], 'Expected one static ET_EXEC header')
    for symbol in FORBIDDEN:
        require(re.search(r'(?<!\S)' + re.escape(symbol) + r'(?!\S)', elf) is None,
                'Diagnostic symbol in ordinary image: ' + symbol)
    section, zero = _bss(elf, layout)
    objects = {}
    for key, symbol, name in OBJECTS:
        address, size, index = _symbol(elf, symbol)
        require(size == sizes[name] and address % aligns[name] == 0 and index == section and
                zero['start'] <= address < address + size <= zero['end'],
                'Ordinary object leaves initialized BSS or violates type: ' + key)
        objects[key] = dict(symbol=symbol, type=name, address=address, bytes=size,
                            alignment=aligns[name], section=index)
    a, b = objects['runtime'], objects['motor_port']
    require(a['address'] + a['bytes'] <= b['address'] or b['address'] + b['bytes'] <= a['address'],
            'Ordinary static objects overlap')
    return objects


def _windows(blocks, runtime, sizes, aligns):
    windows, ranges = {}, []
    for member, name in ABI_WINDOWS.items():
        offset = _numeric(blocks, 'OFFSET', member)
        address, size = runtime['address'] + offset, sizes[name]
        require(offset + size <= runtime['bytes'] and address % aligns[name] == 0,
                'Ordinary window leaves runtime or violates alignment: ' + member)
        ranges.append((offset, offset + size))
        windows[member] = dict(object='runtime', type=name, offset=offset, address=address,
                               bytes=size, alignment=aligns[name])
    ranges.sort()
    require(all(a[1] <= b[0] for a, b in zip(ranges, ranges[1:])), 'Ordinary windows overlap')
    return windows


def _ordinary_summary(result, layout, *, checked_command):
    elf, debug = _streams(result, checked_command)
    blocks = _debug_blocks(debug)
    sizes, aligns, layouts = _type_observations(blocks)
    objects = _objects(elf, layout, sizes, aligns)
    windows = _windows(blocks, objects['runtime'], sizes, aligns)
    enums = {}
    for name, members in ENUMS.items():
        enums[name] = {member: _numeric(blocks, 'ENUM', name + '::' + member) for member in members}
        require(enums[name] == members, 'Ordinary enum values differ: ' + name)
    return dict(schema='ordinary-app-static-abi-v1', status='STATIC_ABI_OBSERVED',
                objects=objects, sizes=sizes, alignments=aligns, layouts=layouts,
                windows=windows, enums=enums,
                limitation='File layout only; no MCU contents, coherent snapshot, runtime, timing or physical acceptance')


def load_reader(*, root=ROOT):
    root = Path(root).absolute()
    snapshots = {}
    for name, identity in ORIGINALS.items():
        snapshots[name] = pinned(root / name, identity[1])
        _verify(snapshots[name], identity, name)
    pinned(root / CONTRACT, CONTRACT_SHA)
    reader = types.ModuleType('_sumox_d209_ordinary_abi')
    reader.__file__ = str(root / BASE)
    exec(compile(project_reader(snapshots[BASE]), reader.__file__, 'exec'), reader.__dict__)
    reader.pinned = pinned
    reader._ordinary_queries = _ordinary_queries
    reader._ordinary_summary = _ordinary_summary
    reader.HARD_PINS = dict(reader.HARD_PINS)
    reader.HARD_PINS.update({name: identity[1] for name, identity in ORIGINALS.items()})
    reader.HARD_PINS[CONTRACT] = CONTRACT_SHA
    return reader


def main(argv):
    require(type(argv) is list and all(type(item) is str for item in argv),
            'Expected an exact argument list')
    require(len(argv) == 3 and argv[0] in ('--check-only', '--execute') and
            argv[1] == '--reviewed-head' and re.fullmatch('[0-9a-f]{40}', argv[2]),
            'Expected --check-only|--execute --reviewed-head <40lowerhex>')
    require(sys.dont_write_bytecode, 'Python -B required')
    return load_reader(root=ROOT).main(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
