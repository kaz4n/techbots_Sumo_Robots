# Audits only archived bytes from the consumed exact default-app observation.
# Rechecks capture identities, read purposes, allocations and literal live samples.
# Uses no subprocess, network, board, MCU, firmware or capture operation.
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import struct
import sys

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[4]
RAW=ROOT/'state/analysis/P2_app_default_probe_raw'
CAP=RAW/'actual_capture'
sys.path.insert(0,str(ROOT/'tools'))
import p0_capture
import recorder_heap
import app_default_capture

def digest(blob): return hashlib.sha256(blob).hexdigest()
def read(path): return json.loads(path.read_text(encoding='utf-8'))
def blob(name): return (CAP/name).read_bytes()
summary=dict(started_utc=datetime.now(timezone.utc).isoformat(),scope='OFFLINE_ARCHIVED_ACTUAL_EVIDENCE_ONLY',checks=0)
def check(value,detail):
    summary['checks']+=1
    if not value: raise AssertionError(detail)

def chain(data):
    check(len(data)==262144,'pool length')
    check(struct.unpack_from('<HH',data)==(0,21),'chunk0')
    check(struct.unpack_from('<I',data,8)[0]==32767,'end chunk')
    at,previous=10,10
    chunks=[]
    spans=[(0,4),(8,68)]
    for _ in range(32768):
        left,bits=struct.unpack_from('<HH',data,at*8)
        size,used=bits>>1,bool(bits&1)
        check(left==previous,'left chain')
        if at==32767:
            check(size==0 and used,'footer')
            spans.append((at*8,4)); break
        check(size>0 and at+size<=32767,'chunk bound')
        chunks.append(dict(index=at,size_units=size,used=used,payload_bytes=size*8-4))
        spans.append((at*8,4 if used else 8))
        previous=size; at+=size
    else: raise AssertionError('unbounded chunk walk')
    metadata=b'SUMOX26_LLEXT_HEAP_METADATA_V1\0'+struct.pack('<II',0x20013890,262144)
    metadata+=b''.join(struct.pack('<II',start,length)+data[start:start+length] for start,length in spans)
    free=sum(c['payload_bytes'] for c in chunks if not c['used'])
    largest=max((c['payload_bytes'] for c in chunks if not c['used']),default=0)
    return chunks,free,largest,digest(metadata)

def contained(chunks,address,size,alignment=4):
    check(address%alignment==0 and 0x20000000<=address<=address+size<=0x200c0000,'SRAM extent/alignment')
    owners=[c for c in chunks if c['used'] and 0x20013890+c['index']*8+4<=address and address+size<=0x20013890+(c['index']+c['size_units'])*8]
    check(len(owners)==1,'one containing allocation')

def literal_sample(data,runtime):
    check(len(data)==(28 if runtime else 24),'prefix length')
    flags=('fresh','initialization_complete','raw_lines','imu_expired','calibration_interrupted') if runtime else ('decision_made','finished','timing_valid')
    words=('next_release_us','missed_releases','epochs','service_passes','maximum_execution_us') if runtime else ('started_us','decision_us','completed_us','execution_us')
    result=dict(phase=data[0],fault=data[1])
    result.update(zip(flags,data[2:2+len(flags)]))
    result.update(zip(words,struct.unpack_from('<'+'I'*len(words),data,8)))
    return result

try:
    archive=read(RAW/'run01_file_archive.json')
    check(archive['status']=='ARCHIVED' and archive['returncode']==0,'archive completion')
    expected={entry['name']:entry for entry in archive['files']}
    check(len(expected)==len(archive['files']) and set(expected)=={p.name for p in CAP.iterdir()},'archive complete exact set')
    for name,item in expected.items():
        path=CAP/name; data=path.read_bytes()
        check(path.is_file() and not path.is_symlink() and len(data)==item['bytes'] and digest(data)==item['sha256'],'archive raw hash '+name)
    check(sum(v['bytes'] for v in expected.values())==archive['bytes'],'archive bytes')
    summary['archive']=dict(files=len(expected),bytes=archive['bytes'],manifest_sha256=digest((RAW/'run01_file_archive.json').read_bytes()))
    report=read(CAP/'capture.json'); execution=read(RAW/'run01_execution_outcome.json')
    attempt=read(RAW/'run01_upload_attempt.json'); uploaded=read(RAW/'run01_upload_outcome.json')
    run=read(ROOT/'state/analysis/P2_app_default_probe_run01.json'); approval=read(RAW/'reviewer/run01_approval.json')
    check(attempt['run_id']==run['run_id']=='app-default-e820c0e1-run01','run identity')
    check(attempt['software_commit']==run['software_commit']==approval['software_commit']=='9b4afcb22823ce48cb20cb4cb951cd55229ac1f2','software binding')
    check(attempt['run_record_sha256']==digest((ROOT/'state/analysis/P2_app_default_probe_run01.json').read_bytes()),'run record hash')
    check(attempt['approval_sha256']==digest((RAW/'reviewer/run01_approval.json').read_bytes()),'approval hash')
    check(attempt['review_sha256']==digest((ROOT/'state/reviews/P2_app_default_run01_review.md').read_bytes()),'review hash')
    check(uploaded['returncode']==0 and not uploaded['timed_out'] and uploaded['error'] is None,'upload outcome')
    preparation=read(RAW/'preparations/a35af3cff5e748879ce98be2f26e7662.json')
    checked=read(ROOT/preparation['checked_receipt']/'verified.json')
    check(preparation['phase']=='UPLOAD_COMMAND_SUCCEEDED' and preparation['error'] is None,'preparation outcome')
    check(checked['source_sha256']==attempt['source_sha256'] and checked['artifacts']==attempt['artifact_folder'],'fresh checked artifact binding')
    check(checked['file_sha256'][checked['build_path']+'/app.ino.elf']==attempt['elf_sha256'],'checked ELF')
    check(checked['file_sha256'][checked['artifacts']+'/app.ino.elf-zsk.bin']==attempt['binary_sha256'],'checked ZSK')
    check(all(g['returncode']==0 and g['stdout'].strip()==run['software_commit'] and g['error'] is None for g in preparation['local_git_checks']),'all prelaunch Git checks')
    check([c['kind'] for c in execution['commands']]==['EXACT_GUARDED_UPLOAD','ONE_PASSIVE_CAPTURE'],'single coordinator sequence')
    check(execution['commands'][0]['returncode']==0,'guard exit')
    summary['upload']=dict(checked_receipt=preparation['checked_receipt'],returncode=uploaded['returncode'],git_checks=len(preparation['local_git_checks']))
    check(report['source_sha256']==attempt['source_sha256'] and report['elf_sha256']==attempt['elf_sha256'] and report['zsk_sha256']==attempt['binary_sha256'],'capture identity binding')
    check(report['counts']==dict(reads=len(report['reads']),commands=len(report['commands']),requested_bytes=sum(r['size'] for r in report['reads'])),'capture counts')
    check(report['counts']['reads']<=62 and report['counts']['commands']<=66 and report['counts']['requested_bytes']<=1405088,'purpose-bound budget')
    check(report['duration_seconds']==report['finished_monotonic']-report['started_monotonic'],'duration arithmetic')
    summary['capture']=dict(status=report['collection_status'],counts=report['counts'],duration_seconds=report['duration_seconds'],coordinator_returncode=execution['commands'][1].get('returncode'),errors=report['errors'])
    metadata=[[str(app_default_capture.OPENOCD),'--version'],[str(app_default_capture.READELF),'--version'],[str(app_default_capture.READELF),'-h','-S','-W',str(app_default_capture.ELF_PATH)],[str(app_default_capture.READELF),'-s','-W',str(app_default_capture.ELF_PATH)]]
    for command,argv in zip(report['commands'][:4],metadata):
        check(command['argv']==argv and command['attach'] is False,'fixed metadata command')
    for i,command in enumerate(report['commands']):
        for label in ('stdout','stderr'):
            data=blob(command[label+'_file'])
            check(len(data)==command[label+'_bytes'] and digest(data)==command[label+'_sha256'],'command retained output')
        check(0<command['timeout_seconds']<=30,'command bound')
        check(command['started_monotonic']-report['started_monotonic']<600,'command start within lifetime')
    by_purpose={r['purpose']:r for r in report['reads']}
    check(len(by_purpose)==len(report['reads']),'no repeated purpose')
    for index,r in enumerate(report['reads']):
        data=blob(r['file'])
        check(len(data)==r.get('bytes_present') and digest(data)==r.get('sha256'),'read raw binding')
        c=report['commands'][index+4]
        config='/home/arduino/sumox26-capture-tools/app-default-beeffff315b2e28a95a20dc1e26477fc924b2da26d1fdd8a8b36fb013ca110e1/p0_mem_read.cfg'
        expected_command=[str(app_default_capture.OPENOCD),'-f',config,'-c',f'dump_image {{{report["output_directory"]}/{r["file"]}}} 0x{r["address"]:08x} {r["size"]}','-c','shutdown']
        check(c['argv']==expected_command and c['attach'] is True,'read-only command surface')
    def data(purpose): return blob(by_purpose[purpose]['file'])
    if report['collection_status']=='CAPTURED':
        check(report['duration_seconds']<600 and not report['errors'],'complete lifetime')
        check(all(c['returncode']==0 for c in report['commands']),'complete command statuses')
        check(all(len(blob(r['file']))==r['size'] for r in report['reads']),'complete read extents')
        loader_path=ROOT/'state/analysis/P2_ui_adc_probe_raw/root_capture_inputs/zephyr-arduino_uno_q_stm32u585xx.elf'
        loader_raw=loader_path.read_bytes(); check(digest(loader_raw)=='39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd','loader ELF reference')
        references={'loader':p0_capture.loader_image(loader_raw),'sketch':(ROOT/'state/analysis/P2_dump_fifo_raw/target_e820c0e1_bench-default/app.ino.elf-zsk.bin').read_bytes()}
        check(digest(references['sketch'])==attempt['binary_sha256'],'sketch reference')
        for what,ref in references.items():
            for when in ('before','after'):
                pieces=[]
                for number in range((len(ref)+65535)//65536):
                    purpose=f'{what}-{when}-{number:02d}'
                    r=by_purpose[purpose]
                    check(r['address']==(0x08000000 if what=='loader' else 0x08100000)+65536*number,'flash exact address')
                    pieces.append(data(purpose))
                check(b''.join(pieces)==ref,'complete full-flash '+what+' '+when)
        pools=[b''.join(data(f'pool-{n}-{i:02d}') for i in range(16)) for n in (1,2)]
        for n in (1,2):
            for i in range(16):
                r=by_purpose[f'pool-{n}-{i:02d}']
                check(r['address']==0x20013890+i*16384 and r['size']==16384,'pool fixed block')
        for when in ('before','after'):
            for purpose,address,size in [('heap-descriptor',0x2000112c,24),('llext-list',0x200017bc,8)]:
                r=by_purpose[purpose+'-'+when]
                check(r['address']==address and r['size']==size,'fixed descriptor/list extent')
        heaps=[recorder_heap.decode_pool(p) for p in pools]
        check(heaps==[report['heap']['before'],report['heap']['after']],'retained heap decoder values')
        comparison=recorder_heap.compare_pools(*pools)
        check(comparison==report['heap']['comparison'],'canonical metadata comparison')
        independent=[chain(p) for p in pools]
        for view,heap in zip(independent,heaps):
            check(view[0]==heap['chunks'] and view[1]==heap['free_payload_bytes'] and view[2]==heap['largest_free_payload_bytes'] and view[3]==heap['metadata_sha256'],'independent chunk walk accounting')
        check(data('heap-descriptor-before')==data('heap-descriptor-after'),'descriptor stability')
        check(struct.unpack_from('<III',data('heap-descriptor-before'))==(0x20013890,0x20013890,262144),'descriptor literal bounds')
        check(data('llext-list-before')==data('llext-list-after'),'list stability')
        node_purposes=[p for p in by_purpose if p.startswith('node-before-')]
        next_address,tail=struct.unpack('<II',data('llext-list-before'))
        node_list=[]; sketch=None
        for i,p in enumerate(node_purposes,1):
            address=by_purpose[p]['address']; node=data(p)
            check(address==next_address and address not in [n['address'] for n in node_list],'bounded list walk')
            check(node==data(f'node-after-{i}'),'node bracket')
            for view in independent: contained(view[0],address,196)
            check(b'\0' in node[4:20],'node name terminated')
            name=node[4:20].split(b'\0',1)[0]
            node_list.append(dict(address=address,name_hex=name.hex()))
            next_address=struct.unpack_from('<I',node)[0]
            if name==b'sketch':
                check(sketch is None,'unique sketch')
                bss=struct.unpack_from('<I',node,32)[0]
                check(node[71]==1 and struct.unpack_from('<I',node,92)[0]==167272,'owned BSS extent')
                check(struct.unpack_from('<II',node,184)==(16,0x0812ad30) and node[192]==0,'resident table')
                sketch=dict(node_address=address,bss_address=bss,runtime_address=bss)
                for view in independent:
                    contained(view[0],bss,167272,8); contained(view[0],bss,166376,8)
        check(len(node_list)<=3 and next_address==0 and tail==(node_list[-1]['address'] if node_list else 0),'tail and terminal link')
        check(node_list==report['extension']['nodes'] and sketch==report['extension']['sketch'],'retained extension identity')
        flashes=lambda when:[f'{what}-{when}-{i:02d}' for what,count in [('loader',5),('sketch',3)] for i in range(count)]
        purposes=flashes('before')+['heap-descriptor-before']+[f'pool-1-{i:02d}' for i in range(16)]+['llext-list-before']
        purposes+=[f'node-before-{i+1}' for i in range(len(node_list))]
        if sketch is not None: purposes+=['runtime-first','transaction-first']
        purposes+=[f'pool-2-{i:02d}' for i in range(16)]+['heap-descriptor-after']
        if sketch is not None: purposes+=['runtime-second','transaction-second']
        purposes+=[f'node-after-{i+1}' for i in range(len(node_list))]+['llext-list-after']+flashes('after')
        check(list(by_purpose)==purposes,'complete exact finite purpose ordering')
        if sketch is not None:
            sample_blobs=[data(p) for p in ('runtime-first','transaction-first','runtime-second','transaction-second')]
            decoded=app_default_capture.decode_app_samples(*sample_blobs)
            check(decoded==report['app_samples'],'pure prefix decoder reproduction')
            literal=[literal_sample(b,i%2==0) for i,b in enumerate(sample_blobs)]
            for i,values in enumerate(literal):
                retained=decoded['runtime' if i%2==0 else 'transaction'][i//2]
                check(all(retained[k]==v for k,v in values.items()),'independent literal prefix words')
                p=('runtime-first','transaction-first','runtime-second','transaction-second')[i]
                offset=164664 if i%2==0 else 162128
                check(by_purpose[p]['address']==sketch['bss_address']+offset,'prefix actual address')
                for view in independent: contained(view[0],by_purpose[p]['address'],len(sample_blobs[i]))
            summary['literal_samples']=literal
            summary['observed_runtime']=decoded['runtime_observation']
            summary['transaction_fault_sampled']=decoded['transaction_fault_sampled']
        else:
            check(report['extension']['status']=='ABSENT' and report['app_samples'] is None,'honest absence')
            summary['observed_runtime']='ABSENT'
        summary['heap']=dict(free_payload_bytes=heaps[0]['free_payload_bytes'],largest_free_payload_bytes=heaps[0]['largest_free_payload_bytes'],metadata_sha256=heaps[0]['metadata_sha256'],snapshot_equal=pools[0]==pools[1],chunks=heaps[0]['chunks'])
        summary['extension']=report['extension']
    else:
        check(report['extension']['status']=='UNKNOWN' and report['extension']['sketch'] is None,'honest failed collection')
        summary['observed_runtime']='INCOMPLETE_CAPTURE'
    summary['verdict']='PASS_OFFLINE_ACTUAL_EVIDENCE_INTEGRITY_REVIEW'
except BaseException as error:
    summary.update(verdict='AUDIT_FAILED',error=repr(error))
    raise
finally:
    summary['finished_utc']=datetime.now(timezone.utc).isoformat()
    path=Path(__file__).parent/sys.argv[1]
    with path.open('x',encoding='utf-8') as stream: json.dump(summary,stream,indent=2); stream.write('\n')
print(json.dumps(summary,indent=2))
