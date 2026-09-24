# Independently rechecks frozen MATCH native evidence using only local bytes.
# Keeps conditional allocator arithmetic separate from compiler and runtime claims.
# Rehashes inputs and decodes ELF directly without importing the author's model.
from pathlib import Path
import hashlib
import json
import re
import struct

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / 'state/analysis/P5_match_native_raw'
OUT = Path(__file__).resolve().parent


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_index():
    index = read(RAW / 'validation_index.json')
    checked, total = 0, 0
    for name, expected in index['files'].items():
        path = RAW / name
        assert path.resolve().is_relative_to(RAW.resolve()) and path.is_file()
        assert sha(path) == expected['sha256'] and path.stat().st_size == expected['bytes'], name
        checked += 1
        total += path.stat().st_size
    for name, expected in index['dependencies'].items():
        path = ROOT / name
        assert path.resolve().is_relative_to(ROOT.resolve()) and path.is_file()
        assert sha(path) == expected['sha256'] and path.stat().st_size == expected['bytes'], name
    assert checked == index['raw_file_count'] == 42 and total == index['raw_total_bytes']
    return dict(index_sha256=sha(RAW / 'validation_index.json'), indexed_files=checked,
                dependencies=len(index['dependencies']), indexed_bytes=total)


def bind_source(receipt):
    source = read(RAW / 'app/source_manifest.json')
    working = read(RAW / 'working_source_manifest.json')
    compile_run = read(RAW / 'compile.json')
    assert sha(RAW / 'working_source_manifest.json') == compile_run['working_source_manifest_sha256']
    assert len(working['files']) == working['file_count'] == 133
    digest = hashlib.sha256()
    for name, expected in sorted(source['files'].items()):
        original = 'src/app/app.ino' if name == 'app.ino' else name
        data = (ROOT / original).read_bytes()
        assert hashlib.sha256(data).hexdigest() == expected == working['files'][original]['sha256'], original
        assert len(data) == working['files'][original]['bytes']
        digest.update(name.encode() + b'\0' + data)
    assert len(source['files']) == 102 and digest.hexdigest() == source['source_sha256'] == receipt['source_sha256']
    return dict(staged_files=102, working_manifest_entries=133, staged_source_sha256=digest.hexdigest(),
                current_staged_bytes_match=True, manifest_git_head=working['git_head'], production_commit=working['production_commit'])


def decode_elf():
    raw = (RAW / 'app/app.ino.elf').read_bytes()
    header = struct.unpack_from('<16sHHIIIIIHHHHHH', raw)
    assert header[0][:6] == b'\x7fELF\x01\x01' and header[1:3] == (1, 40) and header[11] == 40
    sections = [struct.unpack_from('<10I', raw, header[6] + i * 40) for i in range(header[12])]
    strings = sections[header[13]]
    names = raw[strings[4]:strings[4] + strings[5]]
    text = lambda data, offset: data[offset:data.index(b'\0', offset)].decode()
    decoded = [dict(name=text(names, s[0]), type=s[1], flags=s[2], offset=s[4], size=s[5],
                    link=s[6], info=s[7], alignment=s[8], entry=s[9]) for s in sections]
    tables, symbols = {}, []
    for index, section in enumerate(decoded):
        if section['type'] != 2:
            continue
        assert section['entry'] == 16
        string_section = decoded[section['link']]
        names = raw[string_section['offset']:string_section['offset'] + string_section['size']]
        table = []
        for offset in range(section['offset'], section['offset'] + section['size'], 16):
            name, value, size, info, _, index_value = struct.unpack_from('<IIIBBH', raw, offset)
            table.append(dict(name=text(names, name), value=value, size=size, bind=info >> 4,
                              type=info & 15, section=index_value))
        tables[index] = table
        symbols.extend(table)
    imports = set()
    for section in decoded:
        if section['type'] == 9:
            assert section['entry'] == 8
            for offset in range(section['offset'], section['offset'] + section['size'], 8):
                _, info = struct.unpack_from('<II', raw, offset)
                symbol = tables[section['link']][info >> 8]
                if symbol['section'] == 0:
                    imports.add(symbol['name'])
    return decoded, symbols, sorted(imports), header[6]


def arithmetic(sections, symbols, section_header_offset):
    account = read(RAW / 'app/loader_account.json')
    ordered = read(RAW / 'app/ordered_account.json')
    round8 = lambda n: (n + 7) // 8 * 8
    copied = [s for s in sections if s['flags'] & 2 and s['name'] != '.llext.rodata.noreloc' and s['size']]
    chunks = []
    for section in copied:
        alignment = section['alignment']
        assert alignment <= 8
        prepad = section['offset'] % alignment if alignment else 0
        assert prepad == 0
        chunk = 8 + round8(section['size']) if alignment == 8 else round8(section['size'] + 4)
        chunks.append(dict(name=section['name'], payload=section['size'], alignment=alignment, chunk=chunk))
    globals_count = sum(s['bind'] == 1 and s['type'] in (1, 2) for s in symbols)
    exported = next(s['size'] for s in sections if s['name'] == '.exported_sym')
    metadata = dict(initial_bookkeeping=88, extension=round8(196 + 4), section_map=round8(len(sections) * 8 + 4),
                    global_symbols=round8(globals_count * 8 + 4), export_copy=round8(exported + 4))
    payload = sum(s['size'] for s in copied)
    peak = sum(s['chunk'] for s in chunks) + sum(metadata.values())
    assert metadata == account['metadata_chunks'] and globals_count == account['global_func_object_count']
    assert payload == account['compiler_payload'] == 255752 and peak == account['conditional_pristine_peak_consumption'] == 260560
    by_name = {s['name']: s['chunk'] for s in chunks}
    expected_order = [('extension', metadata['extension']), ('section_map', metadata['section_map'])]
    expected_order += [(name, by_name[name]) for name in ('.text', '.data', '.rodata', '.bss', '.exported_sym', '.preinit_array', '.init_array', '.fini_array') if name in by_name]
    expected_order += [('global_symbols', metadata['global_symbols']), ('export_copy', metadata['export_copy'])]
    used = 88
    for (purpose, chunk), row in zip(expected_order, ordered['ordered_allocations']):
        assert row == dict(purpose=purpose, chunk=chunk, available_before=262144 - used, fits=True)
        assert chunk <= 262144 - used
        used += chunk
    assert len(expected_order) == len(ordered['ordered_allocations']) and used == peak
    for section in sections:
        if section['name'] in ('.llext.rodata.noreloc', '.symtab', '.strtab', '.shstrtab'):
            assert (0x08100010 + section['offset']) % section['alignment'] == 0
    assert (0x08100010 + section_header_offset) % 4 == 0
    prior = read(ROOT / 'state/analysis/P5_native_compile_raw/app/loader_account.json')
    assert payload - prior['compiler_payload'] == -1568 and peak - prior['conditional_pristine_peak_consumption'] == -1616
    return dict(section_count=len(sections), globals_count=globals_count, copied_regions=chunks, metadata_chunks=metadata,
                payload=payload, compiler_nominal_remaining=262144 - payload, peak=peak,
                modeled_free_span=262144 - peak, largest_payload=262144 - peak - 4,
                additional_overhead=peak - payload, peek_alignment_checked=True)


def receipts_and_imports(receipt, imports):
    commands = [json.loads(line) for line in (RAW / 'actual_remote_commands.jsonl').read_text().splitlines()]
    compiles = [r for r in commands if r['argv'][:2] == ['arduino-cli', 'compile'] and '--show-properties=expanded' not in r['argv']]
    assert len(compiles) == 1 and compiles[0]['returncode'] == 0
    argv = compiles[0]['argv']
    assert argv[2:4] == ['--jobs', '1'] and '--upload' not in argv
    assert 'compiler.cpp.extra_flags=-DMATCH=1 -DMOTORS_ALLOWED=1' in argv
    assert 'compiler.c.extra_flags=-DMATCH=1 -DMOTORS_ALLOWED=1' in argv
    assert 'build.library_discovery_phase_flag=-DARDUINO_LIBRARY_DISCOVERY_PHASE=0' in argv
    declared = read(RAW / 'app/receipt/compile.command.json')
    assert argv[:2] + argv[4:] == declared
    assert receipt['fqbn'] == 'arduino:zephyr:unoq:wait_linux_boot=no' and receipt['compiler_returncode'] == 0
    compilation = read(RAW / 'app/receipt/compile.stdout.json')
    assert compilation['success'] and '255752 bytes' in compilation['compiler_out'] and '6392 bytes' in compilation['compiler_out']
    captured = read(RAW / 'import_exports.json')
    assert captured['returncode'] == captured['hash_returncode'] == 0
    values = re.findall(r'IMPORT (\S+)\s+\$\d+ = (0x[0-9a-fA-F]+)', captured['stdout'])
    addresses = {name: int(value, 16) for name, value in values}
    assert len(values) == len(addresses) == len(imports) == 62
    assert sorted(addresses) == imports == captured['used_imports'] and addresses == captured['addresses'] and all(addresses.values())
    args = captured['argv']
    assert args[1:4] == ['-nx', '-nh', '-batch']
    expected_queries = []
    for name in imports:
        expected_queries += ['-ex', 'echo IMPORT ' + name + '\\n', '-ex', 'p/x __llext_sym_' + name + '.addr']
    assert args[5:] == expected_queries
    hashes = dict((line.split()[1], line.split()[0]) for line in captured['hash_stdout'].splitlines())
    assert hashes[args[4]] == receipt['file_sha256'][args[4]] == captured['expected_loader_sha256']
    for filename, field in (('account_run.json', 'account_target.py'), ('import_run.json', 'collect_imports.py')):
        run = read(RAW / filename)
        assert run['returncode'] == 0 and run['script_sha256'] == sha(RAW / field)
    return dict(archived_compiles=1, exact_jobs=1, fqbn=receipt['fqbn'], used_imports=len(imports),
                captured_gdb_queries_file_only=True, loader_sha256=hashes[args[4]], gdb_sha256=hashes[args[0]])


def main():
    index_before = verify_index()
    receipt = read(RAW / 'app/receipt/verified.json')
    sections, symbols, imports, section_header_offset = decode_elf()
    elf_hash = sha(RAW / 'app/app.ino.elf')
    assert elf_hash == receipt['file_sha256'][receipt['build_path'] + '/app.ino.elf']
    objects = {s['name']: s['size'] for s in symbols if s['type'] == 1 and s['size'] >= 100}
    assert 166304 in objects.values() and 848 in objects.values() and 208 in objects.values()
    names = {s['name'] for s in symbols}
    assert any('startOpener' in n for n in names) and any('runOpener' in n for n in names)
    assert not any('OpenerTiming' in n or 'OpenerAbort' in n for n in names)
    result = dict(verdict='PASS_CONDITIONAL_SCOPE_REVIEW', index=index_before, source=bind_source(receipt),
                  ELF_sha256=elf_hash, ELF_bytes=(RAW / 'app/app.ino.elf').stat().st_size,
                  account=arithmetic(sections, symbols, section_header_offset),
                  receipts=receipts_and_imports(receipt, imports), static_objects=objects,
                  source_model_imported=False, board_network_compiler_actions=0,
                  script_sha256=sha(Path(__file__)))
    assert verify_index() == index_before
    result['indexed_inputs_unchanged_after'] = True
    target = OUT / 'check_result.json'
    with target.open('x', encoding='utf-8') as output:
        json.dump(result, output, indent=2)
        output.write('\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
