# Preserves and normalizes only the independently tested native fixture sources.
# Proves per-line equivalence and keeps the extractor's sole added formatting pass explicit.
# Writes complete worktree/commit snapshots and hashes before any fixture mutation.
from pathlib import Path
import ast, hashlib, json, re, subprocess, zipfile

root=Path.cwd()
evidence=root/'state/analysis/P2_power_raw'
base=evidence/'fixture_normalization'
commit='e6b7060'
paths=sorted([p for p in (root/'tests/native_power').rglob('*') if p.is_file()]+[root/'tests/tooling/test_power_unoq.py'])
# Refuse to overwrite a prior receipt or snapshot.
zip_path=base.with_suffix('.before.zip')
manifest_path=base.with_suffix('.json')
if zip_path.exists() or manifest_path.exists(): raise RuntimeError('Normalization evidence already exists')
def digest(b): return hashlib.sha256(b).hexdigest()
def lf(b): return b.replace(b'\r\n',b'\n')
def canonical(b):
    lines=lf(b).split(b'\n')
    lines=[line.rstrip(b' \t') for line in lines]
    while lines and not lines[-1]: lines.pop()
    return b'\n'.join(lines)+b'\n'
def eol(b):
    return {'crlf':b.count(b'\r\n'),'lf_only':b.count(b'\n')-b.count(b'\r\n'),'bare_cr':b.count(b'\r')-b.count(b'\r\n')}
original={}
rows=[]
with zipfile.ZipFile(zip_path,'w',compression=zipfile.ZIP_DEFLATED) as z:
    for p in paths:
        rel=p.relative_to(root).as_posix()
        before=p.read_bytes()
        git=subprocess.run(['git','show',f'{commit}:{rel}'],check=True,capture_output=True).stdout
        original[rel]=(before,git)
        z.writestr('worktree/'+rel,before)
        z.writestr('git_'+commit+'/'+rel,git)
        rows.append({'path':rel,'before_worktree_sha256':digest(before),'before_worktree_bytes':len(before),
                     'git_reviewed_sha256':digest(git),'git_reviewed_bytes':len(git),
                     'before_eol':eol(before),'git_eol':eol(git),
                     'worktree_equals_reviewed_after_crlf_to_lf':lf(before)==git})
# Reopen and compare every preserved byte before editing any file.
with zipfile.ZipFile(zip_path) as z:
    for rel,(before,git) in original.items():
        assert z.read('worktree/'+rel)==before
        assert z.read('git_'+commit+'/'+rel)==git
snapshot={'commit':commit,'zip':zip_path.name,'zip_sha256':digest(zip_path.read_bytes()),
          'scope':'29 fixture/runner worktree files and corresponding reviewed Git blobs',
          'files':rows,'status':'SNAPSHOT_VERIFIED_BEFORE_MUTATION'}
manifest_path.write_text(json.dumps(snapshot,indent=2)+'\n',encoding='utf-8')
for p in paths:
    rel=p.relative_to(root).as_posix();before=original[rel][0];after=canonical(before)
    before_lines=lf(before).split(b'\n');after_lines=after.split(b'\n')
    # Removal must never turn a previously noncontinuing line into a continuation.
    for i,line in enumerate(after_lines):
        assert line.endswith(b'\\')==before_lines[i].endswith(b'\\'),(rel,i+1,'continuation drift')
    if after!=before:p.write_bytes(after)
# The only non-whitespace source edit makes regeneration retain this exact form.
extractor=root/'tests/native_power/extract_bits.py'
extra=("for path in [out/'installed_bits.h', out/'installed_types.h', "
       "*[out/f'stm32u5xx_ll_{kind}.h' for kind in selections]]:\n"
       "    path.write_bytes(('\\n'.join(line.rstrip(' \\t') for line in path.read_text().splitlines())"
       ".rstrip('\\n')+'\\n').encode('utf-8'))\n")
normalized_generator=extractor.read_bytes()
extractor.write_bytes(normalized_generator+extra.encode('utf-8'))
before_ast=ast.parse(normalized_generator.decode('utf-8'))
after_ast=ast.parse(extractor.read_text(encoding='utf-8'))
assert ast.dump(ast.Module(body=after_ast.body[:-1],type_ignores=[]))==ast.dump(before_ast)
assert len(after_ast.body)==len(before_ast.body)+1
compile(extractor.read_text(encoding='utf-8'),str(extractor),'exec')
# Reproduction checks the generator produces byte-identical normalized headers.
pre_generation={p:p.read_bytes() for p in paths}
result=subprocess.run(['python',str(extractor)],capture_output=True,text=True)
assert result.returncode==0,(result.stdout,result.stderr)
for p,expected in pre_generation.items(): assert p.read_bytes()==expected,('generator changed normalized output',str(p))
for row in rows:
    rel=row['path'];p=root/rel;before,git=original[rel];after=p.read_bytes()
    expected=canonical(before)+(extra.encode('utf-8') if rel.endswith('/extract_bits.py') else b'')
    assert after==expected
    row.update({'after_sha256':digest(after),'after_bytes':len(after),'after_eol':eol(after),
                'changed_worktree':after!=before,'changed_from_reviewed_git':after!=git,
                'canonical_reviewed_equals_after':canonical(git)+(extra.encode('utf-8') if rel.endswith('/extract_bits.py') else b'')==after,
                'per_line_nontrailing_bytes_equal':True,'macro_continuation_equivalent':True})
    if rel.endswith('/extract_bits.py'):row['per_line_nontrailing_bytes_equal']='Existing lines equal; one explicit output-normalization loop appended; original AST body equal'
    if p.suffix=='.h' and b'STMicroelectronics' in before:
        notice_before=re.search(rb'/\* Copyright.*?\*/',lf(before),re.S).group()
        notice_after=re.search(rb'/\* Copyright.*?\*/',after,re.S).group()
        assert notice_before==notice_after
        row['vendor_notice_preserved']=True
snapshot.update({'status':'PASS','extractor_added_loop':extra,'extractor_ast_prefix_equal':True,
                 'generator':{'argv':['python','tests/native_power/extract_bits.py'],
                              'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr,
                              'all_outputs_byte_identical':True},
                 'test_scope':'Extractor syntax and exact normalized regeneration only; no driver semantics changed, no broad retest'})
manifest_path.write_text(json.dumps(snapshot,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'files':len(rows),'worktree_byte_changes':sum(r['changed_worktree'] for r in rows),
                  'git_blob_changes':sum(r['changed_from_reviewed_git'] for r in rows),
                  'snapshot_sha256':snapshot['zip_sha256'],'status':snapshot['status']},indent=2))
