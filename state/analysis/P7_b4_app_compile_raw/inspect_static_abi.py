# Observes the fixed inhibited B4 application and retained recorder ABI from files.
# Reuses accepted D209 admission, descriptor, child and closing machinery privately.
# Checked by independent focused fixtures before separately admitted native use.
import base64
import hashlib
import os
from pathlib import Path
import re
import stat
import sys
import types

ROOT = Path(__file__).absolute().parents[3]
PREDECESSOR = 'state/analysis/P7_ordinary_app_static_compile_raw/inspect_static_abi.py'
CONTRACT = 'state/analysis/P7_b4_app_abi_contract.md'
CONTRACT_SHA = 'f1f1469c2967a198446d5e7fb01bb7388cee6450732b9e9dde1a9b244633224e'
ORIGINALS = {'state/analysis/P7_ordinary_app_static_compile_raw/inspect_static_abi.py': (44449, 'f816a52366d7031f860d5cdd93e0715905df4b675a24e89d8dbb1d2b63eda97d'), 'tools/compile_b4_app_static.py': (24356, 'b21527e2cbdb50304ef18d8edd982a5bb8eec6f633d75043bd4e323b7cc59e80'), 'state/analysis/P7_b4_app_compile_raw/inputs_static.json': (13493, 'fc8e6fc1131c1952d5e1809f9dc6fb96763dd5e111749424e9ccfaec9b58d38c'), 'state/analysis/P7_b4_app_compile_raw/native_static01/result.json': (1829, 'b722db17adabafc03f6ad8583bcef9b0f6b7d1def4d3e54962508aad4039567a'), 'state/analysis/P7_b4_app_compile_raw/native_static01/artifacts.json': (9484, '0acaa30a4ba01ac5c9ff8c8fddc66c4bec94e033b1194ec63271f12affb6c085'), 'state/reviews/P7_b4_app_compile_actual_review.md': (8486, '7490c2325668a744ebaf3685a12c24365843be402c2d9dae166a79e4a1e4faad'), 'src/core/stand_sequence.h': (1602, '8e4d3e8f631529555d3adb8031de8ea33f3a221c6326c9a09f13fd6b87f6f843'), 'src/hal/recorder.h': (3247, '51a95f35475c38588acdc7cd12c372f0c11afd482077c556a98c92baa169ffec'), 'src/hal/recorder_frames.h': (2945, '093ef637e29f3f84d685d12842eeb1a0540a21646cb42a9dbfa005a734113d53'), 'src/core/logframe.h': (7841, '18bb21e9bff3765fb216f54b10be2c6e06c6380b551b9cd658ad9cb3f28b4660'), 'src/core/types.h': (4094, '8fec6d334fcb1c631c48ed0a076100d2925fee812706af721bb8a208c8c5b8eb'), 'src/core/fsm.h': (41126, '878e4524d6ceceec2a40b86158b11f8a5c18bd03afe35ee5507241dd89562485'), 'src/app/transaction.h': (3710, 'a3c3f12eb49e517f116560b1efed1376110da0e424f6a1714098fcc3c8a84b19'), 'state/analysis/P7_b4_app_compile_raw/abi_plan01.json': (33706, '874da0a9af0477d3ec94cbbc8f86edc03c68229fa0dc7b0c1bc2c7c7dcdf1037')}
BASE_PROJECTED = (12965, '7fb42d51a3f42f99c7e7890b4f4c1dc90360c2d84c09d3bbde7ccea4d1138aea')
INTERMEDIATE = (12940, '57b5c435fbe3004e781136dd16a09693350a64655762b6881b40cb9a6cff7c09')
PROJECTED = (13204, '069af034c960acc478b11ec8c516da58121a8adf2d936531309d298d7ca3feba')
METADATA_STEPS = ((b'state/analysis/P7_ordinary_app_static_compile_raw', b'state/analysis/P7_b4_app_compile_raw', 1), (b'tools/compile_ordinary_app_static.py', b'tools/compile_b4_app_static.py', 1), (b'ordinary-app-static01', b'b4-app-m0-static01', 1), (b'ordinary-app-abi-static01', b'b4-app-m0-abi-static01', 1), (b'D209_STATIC_FILE_ONLY_ABI', b'D215_STATIC_FILE_ONLY_ABI', 2), (b'40b5c765c01bc1749f6ea4534a4b7f274b681b5fa9295ab6f0c57fbf94d66a89', b'b21527e2cbdb50304ef18d8edd982a5bb8eec6f633d75043bd4e323b7cc59e80', 1), (b'a5e8f8b4b78312245c7cde3e86a39db9073b5ef9e5fa2806a3d39eece8600bb7', b'fc8e6fc1131c1952d5e1809f9dc6fb96763dd5e111749424e9ccfaec9b58d38c', 1), (b'221d02be2de722a8886a142328d3accb147cf1ab89b60ed9857e62fdd303aeb0', b'b722db17adabafc03f6ad8583bcef9b0f6b7d1def4d3e54962508aad4039567a', 1), (b'275ebb61be4a0487fe381d915ec28eea4634926b1d06a627850266f5c0a750e0', b'0acaa30a4ba01ac5c9ff8c8fddc66c4bec94e033b1194ec63271f12affb6c085', 1))
SHAPE_STEPS = ((b"TYPES = ('app::Runtime', 'app::RuntimeReport', 'app::Transaction', 'app::TransactionReport', 'motors::MotorGate', 'motors::UnoQPort', 'motors::Result', 'motors::HaltResult', 'fsm::RobotResult', 'fsm::PreviousTick', 'core::Outputs', 'app::SetupGrants')\n", b"TYPES = ('app::Runtime', 'app::RuntimeReport', 'app::Transaction', 'app::TransactionReport', 'motors::MotorGate', 'motors::UnoQPort', 'motors::Result', 'motors::HaltResult', 'fsm::RobotResult', 'fsm::PreviousTick', 'core::Outputs', 'app::SetupGrants', 'stand_sequence::Report', 'recorder::AttemptRecorder', 'recorder::AttemptSummary', 'recorder::FrameBuffer', 'logframe::EventBuffer', 'logframe::TickStatistics', 'logframe::FrameBytes', 'logframe::EventBytes')\n"), (b"WINDOWS = {'report_': 'app::RuntimeReport', 'transaction_.report_': 'app::TransactionReport', 'transaction_.previous_': 'fsm::PreviousTick', 'transaction_.gate_': 'motors::MotorGate', 'grants_': 'app::SetupGrants', 'attempted_': 'bool'}\n", b"WINDOWS = {'report_': 'app::RuntimeReport', 'transaction_.report_': 'app::TransactionReport', 'transaction_.previous_': 'fsm::PreviousTick', 'transaction_.gate_': 'motors::MotorGate', 'grants_': 'app::SetupGrants', 'attempted_': 'bool', 'transaction_.recorder_': 'recorder::AttemptRecorder'}\n"))
ABI_TYPES = ('app::Runtime', 'app::RuntimeReport', 'app::Transaction', 'app::TransactionReport', 'motors::MotorGate', 'motors::UnoQPort', 'motors::Result', 'motors::HaltResult', 'fsm::RobotResult', 'fsm::PreviousTick', 'core::Outputs', 'app::SetupGrants', 'bool', 'stand_sequence::Report', 'recorder::AttemptRecorder', 'recorder::AttemptSummary', 'recorder::FrameBuffer', 'logframe::EventBuffer', 'logframe::TickStatistics', 'logframe::FrameBytes', 'logframe::EventBytes')
ABI_WINDOWS = {'report_': 'app::RuntimeReport', 'transaction_.report_': 'app::TransactionReport', 'transaction_.previous_': 'fsm::PreviousTick', 'transaction_.gate_': 'motors::MotorGate', 'grants_': 'app::SetupGrants', 'attempted_': 'bool', 'transaction_.recorder_': 'recorder::AttemptRecorder'}
ENUMS = {'app::RuntimePhase': {'NOT_STARTED': 0, 'RUNNING': 1, 'STOPPED': 2, 'FAULT': 3, 'STOP_OBSERVING': 4}, 'app::RuntimeFault': {'NONE': 0, 'PORT': 1, 'CLOCK': 2, 'SERVICE_LIMIT': 3, 'TRANSACTION': 4, 'PROJECTION': 5}, 'app::Phase': {'NOT_INITIALIZED': 0, 'IDLE': 1, 'ACQUIRING': 2, 'DECIDED': 3, 'FAULT': 4}, 'app::Fault': {'NONE': 0, 'SETUP': 1, 'ORDER': 2, 'CLOCK': 3, 'IDENTITY': 4, 'RECEIPT': 5, 'ABORTED': 6}, 'motors::Fault': {'NONE': 0, 'NOT_INITIALIZED': 1, 'PORT': 2, 'IO': 3, 'COMMAND': 4, 'TOKEN': 5, 'STOPPED': 6}, 'core::State': {'BOOT': 0, 'IDLE': 1, 'COUNTDOWN': 2, 'OPENER': 3, 'SEARCH': 4, 'TRACK': 5, 'ATTACK': 6, 'DEFEND_TURN': 7, 'EDGE_ESCAPE': 8, 'REFLANK': 9, 'STOPPED': 10, 'DRIVE_TEST': 11}, 'edge::EscapeFault': {'NONE': 0, 'WHITE_PATTERN': 1, 'REPLAN_LIMIT': 2, 'PERMISSION_LOST': 3, 'INVALID_CONTEXT': 4}, 'stand_sequence::Phase': {'NOT_STARTED': 0, 'DRIVE': 1, 'BRAKE': 2, 'COAST': 3, 'COMPLETE': 4, 'INTERRUPTED': 5, 'FAULT': 6}, 'stand_sequence::Reason': {'NONE': 0, 'STOP': 1, 'EDGE': 2, 'CLOCK_ORDER': 3, 'CLOCK_GAP': 4}, 'recorder::AttemptPhase': {'EMPTY': 0, 'RECORDING': 1, 'DRAINING': 2, 'SEALED': 3, 'INTERRUPTED': 4}, 'logframe::PackStatus': {'OK': 0, 'CLAMPED': 1, 'INVALID': 2}, 'core::Mode': {'SIDESTEP_R': 1, 'SIDESTEP_L': 2, 'DIRECT': 3, 'ARC_R': 4, 'ARC_L': 5, 'WAIT': 6}}
SUBFIELDS = {'robot.stand': 'stand_sequence::Report', 'robot.stand_stopping': 'bool'}
MEMBER_SIZES = {'FrameBuffer.payloads_': ('sizeof(((recorder::FrameBuffer*)0)->payloads_)', 125025), 'FrameBuffer.statuses_': ('sizeof(((recorder::FrameBuffer*)0)->statuses_)', 1251), 'EventBuffer.events_': ('sizeof(((logframe::EventBuffer*)0)->events_)', 32768), 'FrameBuffer.first_': ('sizeof(((recorder::FrameBuffer*)0)->first_)', 4), 'FrameBuffer.size_': ('sizeof(((recorder::FrameBuffer*)0)->size_)', 4), 'EventBuffer.size_': ('sizeof(((logframe::EventBuffer*)0)->size_)', 4), 'stand_sequence::Phase': ('sizeof(stand_sequence::Phase)', 1), 'stand_sequence::Reason': ('sizeof(stand_sequence::Reason)', 1), 'recorder::AttemptPhase': ('sizeof(recorder::AttemptPhase)', 1), 'logframe::PackStatus': ('sizeof(logframe::PackStatus)', 1), 'core::Mode': ('sizeof(core::Mode)', 1)}
CAPACITIES = {'frame_bytes': 25, 'frames': 5001, 'frame_status_bytes': 1251, 'event_bytes': 8, 'events': 4096, 'index_bytes': 4}
PROFILE = {'project': 'app.ino', 'fqbn': 'arduino:zephyr:unoq:link_mode=static', 'flags': '-DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_B4_STAND=1 -DSUMOX_P3_DRIVE_TEST=0 -DSUMOX_P3_TURN_TRIAL=0 -DSUMOX_P3_STOP_TRIAL=0 -DSUMOX_P4_REACTIVE=0 -DSUMOX_TIMING_EVIDENCE=0 -DSUMOX_P5_ABORT_TIMING=0 -DSUMOX_MOTOR_FAULT_PROBE=0', 'source_sha256': '9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a', 'motors_allowed': 0}
OWNER = '/home/arduino/sumox26_codex_build/b4-app-m0-static01'
PREFIX = '/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin/arm-zephyr-eabi-'
EXPRESSIONS = ('set max-value-size 1048576', 'echo SUMOX_SIZE app::Runtime\\n', 'p/d sizeof(app::Runtime)', 'echo SUMOX_ALIGN app::Runtime\\n', 'p/d alignof(app::Runtime)', 'echo SUMOX_LAYOUT app::Runtime\\n', 'ptype /o app::Runtime', 'echo SUMOX_SIZE app::RuntimeReport\\n', 'p/d sizeof(app::RuntimeReport)', 'echo SUMOX_ALIGN app::RuntimeReport\\n', 'p/d alignof(app::RuntimeReport)', 'echo SUMOX_LAYOUT app::RuntimeReport\\n', 'ptype /o app::RuntimeReport', 'echo SUMOX_SIZE app::Transaction\\n', 'p/d sizeof(app::Transaction)', 'echo SUMOX_ALIGN app::Transaction\\n', 'p/d alignof(app::Transaction)', 'echo SUMOX_LAYOUT app::Transaction\\n', 'ptype /o app::Transaction', 'echo SUMOX_SIZE app::TransactionReport\\n', 'p/d sizeof(app::TransactionReport)', 'echo SUMOX_ALIGN app::TransactionReport\\n', 'p/d alignof(app::TransactionReport)', 'echo SUMOX_LAYOUT app::TransactionReport\\n', 'ptype /o app::TransactionReport', 'echo SUMOX_SIZE motors::MotorGate\\n', 'p/d sizeof(motors::MotorGate)', 'echo SUMOX_ALIGN motors::MotorGate\\n', 'p/d alignof(motors::MotorGate)', 'echo SUMOX_LAYOUT motors::MotorGate\\n', 'ptype /o motors::MotorGate', 'echo SUMOX_SIZE motors::UnoQPort\\n', 'p/d sizeof(motors::UnoQPort)', 'echo SUMOX_ALIGN motors::UnoQPort\\n', 'p/d alignof(motors::UnoQPort)', 'echo SUMOX_LAYOUT motors::UnoQPort\\n', 'ptype /o motors::UnoQPort', 'echo SUMOX_SIZE motors::Result\\n', 'p/d sizeof(motors::Result)', 'echo SUMOX_ALIGN motors::Result\\n', 'p/d alignof(motors::Result)', 'echo SUMOX_LAYOUT motors::Result\\n', 'ptype /o motors::Result', 'echo SUMOX_SIZE motors::HaltResult\\n', 'p/d sizeof(motors::HaltResult)', 'echo SUMOX_ALIGN motors::HaltResult\\n', 'p/d alignof(motors::HaltResult)', 'echo SUMOX_LAYOUT motors::HaltResult\\n', 'ptype /o motors::HaltResult', 'echo SUMOX_SIZE fsm::RobotResult\\n', 'p/d sizeof(fsm::RobotResult)', 'echo SUMOX_ALIGN fsm::RobotResult\\n', 'p/d alignof(fsm::RobotResult)', 'echo SUMOX_LAYOUT fsm::RobotResult\\n', 'ptype /o fsm::RobotResult', 'echo SUMOX_SIZE fsm::PreviousTick\\n', 'p/d sizeof(fsm::PreviousTick)', 'echo SUMOX_ALIGN fsm::PreviousTick\\n', 'p/d alignof(fsm::PreviousTick)', 'echo SUMOX_LAYOUT fsm::PreviousTick\\n', 'ptype /o fsm::PreviousTick', 'echo SUMOX_SIZE core::Outputs\\n', 'p/d sizeof(core::Outputs)', 'echo SUMOX_ALIGN core::Outputs\\n', 'p/d alignof(core::Outputs)', 'echo SUMOX_LAYOUT core::Outputs\\n', 'ptype /o core::Outputs', 'echo SUMOX_SIZE app::SetupGrants\\n', 'p/d sizeof(app::SetupGrants)', 'echo SUMOX_ALIGN app::SetupGrants\\n', 'p/d alignof(app::SetupGrants)', 'echo SUMOX_LAYOUT app::SetupGrants\\n', 'ptype /o app::SetupGrants', 'echo SUMOX_SIZE bool\\n', 'p/d sizeof(bool)', 'echo SUMOX_ALIGN bool\\n', 'p/d alignof(bool)', 'echo SUMOX_LAYOUT bool\\n', 'ptype /o bool', 'echo SUMOX_OFFSET report_\\n', 'p/d (unsigned long)&((app::Runtime*)0)->report_', 'echo SUMOX_OFFSET transaction_.report_\\n', 'p/d (unsigned long)&((app::Runtime*)0)->transaction_.report_', 'echo SUMOX_OFFSET transaction_.previous_\\n', 'p/d (unsigned long)&((app::Runtime*)0)->transaction_.previous_', 'echo SUMOX_OFFSET transaction_.gate_\\n', 'p/d (unsigned long)&((app::Runtime*)0)->transaction_.gate_', 'echo SUMOX_OFFSET grants_\\n', 'p/d (unsigned long)&((app::Runtime*)0)->grants_', 'echo SUMOX_OFFSET attempted_\\n', 'p/d (unsigned long)&((app::Runtime*)0)->attempted_', 'echo SUMOX_ENUM app::RuntimePhase::NOT_STARTED\\n', 'p/d (unsigned int)app::RuntimePhase::NOT_STARTED', 'echo SUMOX_ENUM app::RuntimePhase::RUNNING\\n', 'p/d (unsigned int)app::RuntimePhase::RUNNING', 'echo SUMOX_ENUM app::RuntimePhase::STOPPED\\n', 'p/d (unsigned int)app::RuntimePhase::STOPPED', 'echo SUMOX_ENUM app::RuntimePhase::FAULT\\n', 'p/d (unsigned int)app::RuntimePhase::FAULT', 'echo SUMOX_ENUM app::RuntimePhase::STOP_OBSERVING\\n', 'p/d (unsigned int)app::RuntimePhase::STOP_OBSERVING', 'echo SUMOX_ENUM app::RuntimeFault::NONE\\n', 'p/d (unsigned int)app::RuntimeFault::NONE', 'echo SUMOX_ENUM app::RuntimeFault::PORT\\n', 'p/d (unsigned int)app::RuntimeFault::PORT', 'echo SUMOX_ENUM app::RuntimeFault::CLOCK\\n', 'p/d (unsigned int)app::RuntimeFault::CLOCK', 'echo SUMOX_ENUM app::RuntimeFault::SERVICE_LIMIT\\n', 'p/d (unsigned int)app::RuntimeFault::SERVICE_LIMIT', 'echo SUMOX_ENUM app::RuntimeFault::TRANSACTION\\n', 'p/d (unsigned int)app::RuntimeFault::TRANSACTION', 'echo SUMOX_ENUM app::RuntimeFault::PROJECTION\\n', 'p/d (unsigned int)app::RuntimeFault::PROJECTION', 'echo SUMOX_ENUM app::Phase::NOT_INITIALIZED\\n', 'p/d (unsigned int)app::Phase::NOT_INITIALIZED', 'echo SUMOX_ENUM app::Phase::IDLE\\n', 'p/d (unsigned int)app::Phase::IDLE', 'echo SUMOX_ENUM app::Phase::ACQUIRING\\n', 'p/d (unsigned int)app::Phase::ACQUIRING', 'echo SUMOX_ENUM app::Phase::DECIDED\\n', 'p/d (unsigned int)app::Phase::DECIDED', 'echo SUMOX_ENUM app::Phase::FAULT\\n', 'p/d (unsigned int)app::Phase::FAULT', 'echo SUMOX_ENUM app::Fault::NONE\\n', 'p/d (unsigned int)app::Fault::NONE', 'echo SUMOX_ENUM app::Fault::SETUP\\n', 'p/d (unsigned int)app::Fault::SETUP', 'echo SUMOX_ENUM app::Fault::ORDER\\n', 'p/d (unsigned int)app::Fault::ORDER', 'echo SUMOX_ENUM app::Fault::CLOCK\\n', 'p/d (unsigned int)app::Fault::CLOCK', 'echo SUMOX_ENUM app::Fault::IDENTITY\\n', 'p/d (unsigned int)app::Fault::IDENTITY', 'echo SUMOX_ENUM app::Fault::RECEIPT\\n', 'p/d (unsigned int)app::Fault::RECEIPT', 'echo SUMOX_ENUM app::Fault::ABORTED\\n', 'p/d (unsigned int)app::Fault::ABORTED', 'echo SUMOX_ENUM motors::Fault::NONE\\n', 'p/d (unsigned int)motors::Fault::NONE', 'echo SUMOX_ENUM motors::Fault::NOT_INITIALIZED\\n', 'p/d (unsigned int)motors::Fault::NOT_INITIALIZED', 'echo SUMOX_ENUM motors::Fault::PORT\\n', 'p/d (unsigned int)motors::Fault::PORT', 'echo SUMOX_ENUM motors::Fault::IO\\n', 'p/d (unsigned int)motors::Fault::IO', 'echo SUMOX_ENUM motors::Fault::COMMAND\\n', 'p/d (unsigned int)motors::Fault::COMMAND', 'echo SUMOX_ENUM motors::Fault::TOKEN\\n', 'p/d (unsigned int)motors::Fault::TOKEN', 'echo SUMOX_ENUM motors::Fault::STOPPED\\n', 'p/d (unsigned int)motors::Fault::STOPPED', 'echo SUMOX_ENUM core::State::BOOT\\n', 'p/d (unsigned int)core::State::BOOT', 'echo SUMOX_ENUM core::State::IDLE\\n', 'p/d (unsigned int)core::State::IDLE', 'echo SUMOX_ENUM core::State::COUNTDOWN\\n', 'p/d (unsigned int)core::State::COUNTDOWN', 'echo SUMOX_ENUM core::State::OPENER\\n', 'p/d (unsigned int)core::State::OPENER', 'echo SUMOX_ENUM core::State::SEARCH\\n', 'p/d (unsigned int)core::State::SEARCH', 'echo SUMOX_ENUM core::State::TRACK\\n', 'p/d (unsigned int)core::State::TRACK', 'echo SUMOX_ENUM core::State::ATTACK\\n', 'p/d (unsigned int)core::State::ATTACK', 'echo SUMOX_ENUM core::State::DEFEND_TURN\\n', 'p/d (unsigned int)core::State::DEFEND_TURN', 'echo SUMOX_ENUM core::State::EDGE_ESCAPE\\n', 'p/d (unsigned int)core::State::EDGE_ESCAPE', 'echo SUMOX_ENUM core::State::REFLANK\\n', 'p/d (unsigned int)core::State::REFLANK', 'echo SUMOX_ENUM core::State::STOPPED\\n', 'p/d (unsigned int)core::State::STOPPED', 'echo SUMOX_ENUM core::State::DRIVE_TEST\\n', 'p/d (unsigned int)core::State::DRIVE_TEST', 'echo SUMOX_ENUM edge::EscapeFault::NONE\\n', 'p/d (unsigned int)edge::EscapeFault::NONE', 'echo SUMOX_ENUM edge::EscapeFault::WHITE_PATTERN\\n', 'p/d (unsigned int)edge::EscapeFault::WHITE_PATTERN', 'echo SUMOX_ENUM edge::EscapeFault::REPLAN_LIMIT\\n', 'p/d (unsigned int)edge::EscapeFault::REPLAN_LIMIT', 'echo SUMOX_ENUM edge::EscapeFault::PERMISSION_LOST\\n', 'p/d (unsigned int)edge::EscapeFault::PERMISSION_LOST', 'echo SUMOX_ENUM edge::EscapeFault::INVALID_CONTEXT\\n', 'p/d (unsigned int)edge::EscapeFault::INVALID_CONTEXT', 'echo SUMOX_SIZE stand_sequence::Report\\n', 'p/d sizeof(stand_sequence::Report)', 'echo SUMOX_ALIGN stand_sequence::Report\\n', 'p/d alignof(stand_sequence::Report)', 'echo SUMOX_LAYOUT stand_sequence::Report\\n', 'ptype /o stand_sequence::Report', 'echo SUMOX_SIZE recorder::AttemptRecorder\\n', 'p/d sizeof(recorder::AttemptRecorder)', 'echo SUMOX_ALIGN recorder::AttemptRecorder\\n', 'p/d alignof(recorder::AttemptRecorder)', 'echo SUMOX_LAYOUT recorder::AttemptRecorder\\n', 'ptype /o recorder::AttemptRecorder', 'echo SUMOX_SIZE recorder::AttemptSummary\\n', 'p/d sizeof(recorder::AttemptSummary)', 'echo SUMOX_ALIGN recorder::AttemptSummary\\n', 'p/d alignof(recorder::AttemptSummary)', 'echo SUMOX_LAYOUT recorder::AttemptSummary\\n', 'ptype /o recorder::AttemptSummary', 'echo SUMOX_SIZE recorder::FrameBuffer\\n', 'p/d sizeof(recorder::FrameBuffer)', 'echo SUMOX_ALIGN recorder::FrameBuffer\\n', 'p/d alignof(recorder::FrameBuffer)', 'echo SUMOX_LAYOUT recorder::FrameBuffer\\n', 'ptype /o recorder::FrameBuffer', 'echo SUMOX_SIZE logframe::EventBuffer\\n', 'p/d sizeof(logframe::EventBuffer)', 'echo SUMOX_ALIGN logframe::EventBuffer\\n', 'p/d alignof(logframe::EventBuffer)', 'echo SUMOX_LAYOUT logframe::EventBuffer\\n', 'ptype /o logframe::EventBuffer', 'echo SUMOX_SIZE logframe::TickStatistics\\n', 'p/d sizeof(logframe::TickStatistics)', 'echo SUMOX_ALIGN logframe::TickStatistics\\n', 'p/d alignof(logframe::TickStatistics)', 'echo SUMOX_LAYOUT logframe::TickStatistics\\n', 'ptype /o logframe::TickStatistics', 'echo SUMOX_SIZE logframe::FrameBytes\\n', 'p/d sizeof(logframe::FrameBytes)', 'echo SUMOX_ALIGN logframe::FrameBytes\\n', 'p/d alignof(logframe::FrameBytes)', 'echo SUMOX_LAYOUT logframe::FrameBytes\\n', 'ptype /o logframe::FrameBytes', 'echo SUMOX_SIZE logframe::EventBytes\\n', 'p/d sizeof(logframe::EventBytes)', 'echo SUMOX_ALIGN logframe::EventBytes\\n', 'p/d alignof(logframe::EventBytes)', 'echo SUMOX_LAYOUT logframe::EventBytes\\n', 'ptype /o logframe::EventBytes', 'echo SUMOX_OFFSET transaction_.recorder_\\n', 'p/d (unsigned long)&((app::Runtime*)0)->transaction_.recorder_', 'echo SUMOX_SUBOFFSET robot.stand\\n', 'p/d (unsigned long)&((app::TransactionReport*)0)->robot.stand', 'echo SUMOX_SUBOFFSET robot.stand_stopping\\n', 'p/d (unsigned long)&((app::TransactionReport*)0)->robot.stand_stopping', 'echo SUMOX_MEMBER_SIZE FrameBuffer.payloads_\\n', 'p/d sizeof(((recorder::FrameBuffer*)0)->payloads_)', 'echo SUMOX_MEMBER_SIZE FrameBuffer.statuses_\\n', 'p/d sizeof(((recorder::FrameBuffer*)0)->statuses_)', 'echo SUMOX_MEMBER_SIZE EventBuffer.events_\\n', 'p/d sizeof(((logframe::EventBuffer*)0)->events_)', 'echo SUMOX_MEMBER_SIZE FrameBuffer.first_\\n', 'p/d sizeof(((recorder::FrameBuffer*)0)->first_)', 'echo SUMOX_MEMBER_SIZE FrameBuffer.size_\\n', 'p/d sizeof(((recorder::FrameBuffer*)0)->size_)', 'echo SUMOX_MEMBER_SIZE EventBuffer.size_\\n', 'p/d sizeof(((logframe::EventBuffer*)0)->size_)', 'echo SUMOX_MEMBER_SIZE stand_sequence::Phase\\n', 'p/d sizeof(stand_sequence::Phase)', 'echo SUMOX_MEMBER_SIZE stand_sequence::Reason\\n', 'p/d sizeof(stand_sequence::Reason)', 'echo SUMOX_MEMBER_SIZE recorder::AttemptPhase\\n', 'p/d sizeof(recorder::AttemptPhase)', 'echo SUMOX_MEMBER_SIZE logframe::PackStatus\\n', 'p/d sizeof(logframe::PackStatus)', 'echo SUMOX_MEMBER_SIZE core::Mode\\n', 'p/d sizeof(core::Mode)', 'echo SUMOX_ENUM stand_sequence::Phase::NOT_STARTED\\n', 'p/d (unsigned int)stand_sequence::Phase::NOT_STARTED', 'echo SUMOX_ENUM stand_sequence::Phase::DRIVE\\n', 'p/d (unsigned int)stand_sequence::Phase::DRIVE', 'echo SUMOX_ENUM stand_sequence::Phase::BRAKE\\n', 'p/d (unsigned int)stand_sequence::Phase::BRAKE', 'echo SUMOX_ENUM stand_sequence::Phase::COAST\\n', 'p/d (unsigned int)stand_sequence::Phase::COAST', 'echo SUMOX_ENUM stand_sequence::Phase::COMPLETE\\n', 'p/d (unsigned int)stand_sequence::Phase::COMPLETE', 'echo SUMOX_ENUM stand_sequence::Phase::INTERRUPTED\\n', 'p/d (unsigned int)stand_sequence::Phase::INTERRUPTED', 'echo SUMOX_ENUM stand_sequence::Phase::FAULT\\n', 'p/d (unsigned int)stand_sequence::Phase::FAULT', 'echo SUMOX_ENUM stand_sequence::Reason::NONE\\n', 'p/d (unsigned int)stand_sequence::Reason::NONE', 'echo SUMOX_ENUM stand_sequence::Reason::STOP\\n', 'p/d (unsigned int)stand_sequence::Reason::STOP', 'echo SUMOX_ENUM stand_sequence::Reason::EDGE\\n', 'p/d (unsigned int)stand_sequence::Reason::EDGE', 'echo SUMOX_ENUM stand_sequence::Reason::CLOCK_ORDER\\n', 'p/d (unsigned int)stand_sequence::Reason::CLOCK_ORDER', 'echo SUMOX_ENUM stand_sequence::Reason::CLOCK_GAP\\n', 'p/d (unsigned int)stand_sequence::Reason::CLOCK_GAP', 'echo SUMOX_ENUM recorder::AttemptPhase::EMPTY\\n', 'p/d (unsigned int)recorder::AttemptPhase::EMPTY', 'echo SUMOX_ENUM recorder::AttemptPhase::RECORDING\\n', 'p/d (unsigned int)recorder::AttemptPhase::RECORDING', 'echo SUMOX_ENUM recorder::AttemptPhase::DRAINING\\n', 'p/d (unsigned int)recorder::AttemptPhase::DRAINING', 'echo SUMOX_ENUM recorder::AttemptPhase::SEALED\\n', 'p/d (unsigned int)recorder::AttemptPhase::SEALED', 'echo SUMOX_ENUM recorder::AttemptPhase::INTERRUPTED\\n', 'p/d (unsigned int)recorder::AttemptPhase::INTERRUPTED', 'echo SUMOX_ENUM logframe::PackStatus::OK\\n', 'p/d (unsigned int)logframe::PackStatus::OK', 'echo SUMOX_ENUM logframe::PackStatus::CLAMPED\\n', 'p/d (unsigned int)logframe::PackStatus::CLAMPED', 'echo SUMOX_ENUM logframe::PackStatus::INVALID\\n', 'p/d (unsigned int)logframe::PackStatus::INVALID', 'echo SUMOX_ENUM core::Mode::SIDESTEP_R\\n', 'p/d (unsigned int)core::Mode::SIDESTEP_R', 'echo SUMOX_ENUM core::Mode::SIDESTEP_L\\n', 'p/d (unsigned int)core::Mode::SIDESTEP_L', 'echo SUMOX_ENUM core::Mode::DIRECT\\n', 'p/d (unsigned int)core::Mode::DIRECT', 'echo SUMOX_ENUM core::Mode::ARC_R\\n', 'p/d (unsigned int)core::Mode::ARC_R', 'echo SUMOX_ENUM core::Mode::ARC_L\\n', 'p/d (unsigned int)core::Mode::ARC_L', 'echo SUMOX_ENUM core::Mode::WAIT\\n', 'p/d (unsigned int)core::Mode::WAIT')
MARKERS = tuple(expression[5:-2] for expression in EXPRESSIONS if expression.startswith('echo SUMOX_'))
_BUILD = OWNER + '/build/app.ino'
COMMANDS = (
    (PREFIX + 'readelf', '--version'),
    (PREFIX + 'gdb', '--version'),
    (PREFIX + 'readelf', '-hSWs', _BUILD + '.elf'),
    tuple([PREFIX + 'gdb', '-nx', '-nh', '-batch', '-iex', 'set auto-load no',
           _BUILD + '_debug.elf', '-ex', 'set language c++', '-ex', 'set may-call-functions off'] +
          [item for expression in EXPRESSIONS for item in ('-ex', expression)]),
)


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
    _verify(raw, BASE_PROJECTED, 'accepted D209 projected reader')
    for old, new, count in METADATA_STEPS:
        require(raw.count(old) == count, 'B4 ABI metadata occurrence changed')
        raw = raw.replace(old, new)
    _verify(raw, INTERMEDIATE, 'B4 ABI metadata intermediate')
    for old, new in SHAPE_STEPS:
        require(raw.count(old) == 1, 'B4 ABI type/window span changed')
        raw = raw.replace(old, new)
    _verify(raw, PROJECTED, 'B4 ABI projected reader')
    return raw


def _b4_queries(reader):
    build = OWNER + '/build/app.ino'
    commands = [[reader.PREFIX + 'readelf', '--version'],
                [reader.PREFIX + 'gdb', '--version'],
                [reader.PREFIX + 'readelf', '-hSWs', build + '.elf'],
                reader.gdb(build + '_debug.elf', list(EXPRESSIONS))]
    require(commands == [list(command) for command in COMMANDS], 'B4 file commands changed')
    return commands


def _robot_container(layout, sizes, aligns):
    pattern = (r'^/\*\s*([0-9]+)\s*\|\s*([0-9]+)\s*\*/\s*'
               r'struct fsm::RobotResult\s*\{')
    matches = list(re.finditer(pattern, layout, re.MULTILINE))
    require(len(matches) == 1 and len(re.findall(r'\brobot\s*;', layout)) == 1,
            'Missing or duplicate nested RobotResult')
    match = matches[0]
    prefix = layout[:match.start()]
    require(prefix.count('{') - prefix.count('}') == 1, 'RobotResult is not a direct member')
    depth, end = 1, None
    for index in range(match.end(), len(layout)):
        depth += (layout[index] == '{') - (layout[index] == '}')
        if depth == 0:
            end = index
            break
    require(end is not None and re.match(r'\s*robot\s*;', layout[end + 1:]) is not None,
            'Nested RobotResult closing member differs')
    offset, size = int(match[1]), int(match[2])
    require(size == sizes['fsm::RobotResult'] and offset % aligns['fsm::RobotResult'] == 0 and
            offset + size <= sizes['app::TransactionReport'], 'Nested RobotResult extent differs')
    return offset, offset + size


def _stand_fields(parser, blocks, summary):
    sizes, aligns = summary['sizes'], summary['alignments']
    start, end = _robot_container(summary['layouts']['app::TransactionReport'], sizes, aligns)
    parent = summary['windows']['transaction_.report_']
    fields, ranges = {}, []
    for member, name in SUBFIELDS.items():
        offset = parser._numeric(blocks, 'SUBOFFSET', member)
        address, size = parent['address'] + offset, sizes[name]
        require(start <= offset < offset + size <= end and address % aligns[name] == 0,
                'Stand subfield leaves RobotResult or violates alignment')
        fields[member] = dict(parent='transaction_.report_', type=name, offset=offset,
                              address=address, bytes=size, alignment=aligns[name])
        ranges.append((offset, offset + size))
    ranges.sort()
    require(all(a[1] <= b[0] for a, b in zip(ranges, ranges[1:])), 'Stand subfields overlap')
    return fields


def _member_sizes(parser, blocks, sizes):
    values = {name: parser._numeric(blocks, 'MEMBER_SIZE', name) for name in MEMBER_SIZES}
    require(values == {name: item[1] for name, item in MEMBER_SIZES.items()},
            'Unsupported B4 member sizes')
    require(sizes['logframe::FrameBytes'] == 25 and sizes['logframe::EventBytes'] == 8,
            'Unsupported recorder wire widths')
    require(values['FrameBuffer.payloads_'] // 25 == 5001 and
            values['FrameBuffer.statuses_'] == (5001 + 3) // 4 and
            values['EventBuffer.events_'] // 8 == 4096, 'Recorder capacity differs')
    require(sum(values[name] for name in ('FrameBuffer.payloads_', 'FrameBuffer.statuses_',
                'FrameBuffer.first_', 'FrameBuffer.size_')) <= sizes['recorder::FrameBuffer'] and
            values['EventBuffer.events_'] + values['EventBuffer.size_'] <= sizes['logframe::EventBuffer'],
            'Recorder members exceed their parent type')
    require(sizes['recorder::FrameBuffer'] + sizes['logframe::EventBuffer'] +
            sizes['recorder::AttemptSummary'] <= sizes['recorder::AttemptRecorder'] and
            sizes['logframe::TickStatistics'] <= sizes['recorder::AttemptSummary'],
            'Recorder nested types exceed their parent')
    return values


def _b4_summary(parser, result, layout, *, checked_command):
    summary = parser._ordinary_summary(result, layout, checked_command=checked_command)
    debug = base64.b64decode(result['commands'][3]['stdout_base64'], validate=True).decode('utf-8')
    blocks = parser._debug_blocks(debug)
    fields = _stand_fields(parser, blocks, summary)
    members = _member_sizes(parser, blocks, summary['sizes'])
    summary.update(schema='b4-app-m0-static-abi-v1', subfields=fields, member_sizes=members,
                   capacities=dict(CAPACITIES), profile=dict(PROFILE))
    return summary


def load_reader(*, root=ROOT):
    root = Path(root).absolute()
    snapshots = {}
    for name, identity in ORIGINALS.items():
        snapshots[name] = pinned(root / name, identity[1])
        _verify(snapshots[name], identity, name)
    pinned(root / CONTRACT, CONTRACT_SHA)
    parser = types.ModuleType('_sumox_d215_checked_d209')
    parser.__file__ = str(root / PREDECESSOR)
    exec(compile(snapshots[PREDECESSOR], parser.__file__, 'exec'), parser.__dict__)
    original_project = parser.project_reader
    parser.project_reader = lambda raw: project_reader(original_project(raw))
    parser.ABI_TYPES, parser.ABI_WINDOWS = ABI_TYPES, dict(ABI_WINDOWS)
    parser.ENUMS = {name: dict(values) for name, values in ENUMS.items()}
    parser.EXPRESSIONS, parser.MARKERS, parser.COMMANDS = EXPRESSIONS, MARKERS, COMMANDS
    reader = parser.load_reader(root=root)
    reader._ordinary_queries = _b4_queries
    reader._ordinary_summary = lambda result, layout, *, checked_command: _b4_summary(
        parser, result, layout, checked_command=checked_command)
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
