"""Decode original D114 Runner bytes from the adopted public ABI independently.

This module imports no firmware, production capture code or test fixtures.
Its output describes observed bytes and MCU-clock intervals, not physical acceptance.
"""
import argparse
import hashlib
import json
from pathlib import Path
import statistics
import struct

MASK,HALF=0xffffffff,0x80000000
PHASES=('NOT_STARTED','DISABLED','RUNNING','COMPLETE','FAULT')
FAULTS=('NONE','PORT','CONFIG','SETUP','ADC','CONTRACT','SOURCE_ORDER','CLOCK')
STATUS=('OK','NOT_INITIALIZED','ALREADY_STARTED','INVALID_CONFIG','OWNERSHIP',
        'REGULATOR_TIMEOUT','CALIBRATION_TIMEOUT','ENABLE_TIMEOUT','CONVERSION_TIMEOUT',
        'POLL_LIMIT','READBACK','OVERRUN','INVALID_DATA','FAULT_LATCHED','NOT_ENABLED')
QUALIFICATIONS=('ABSENT','VALID','UNCONFIGURED','UNKNOWN','AMBIGUOUS','INVALID')


def sample(blob,offset):
    return dict(zip(('status','shutdown','raw','started_us','completed_us','sequence','valid'),
                    struct.unpack_from('<BBHIIIB',blob,offset)))


def decoded(blob,offset):
    fields=struct.unpack_from('<BBBBH2xIII',blob,offset+4)
    return {'qualification':blob[offset],'candidate_mask':blob[offset+24],
            'evidence':dict(zip(('explicit_values','contract_valid','presence','level',
                                'raw','sequence','started_us','completed_us'),fields))}


def timing(blob,offset):
    return dict(zip(('calls','measured_calls','last_us','maximum_us','last_valid'),
                    struct.unpack_from('<IIIIB',blob,offset)))


def unpack(blob):
    if type(blob) is not bytes or len(blob)!=9892: raise ValueError('Expected9892 immutable bytes')
    names=('phase','fault','fresh','clock_fault','counter_saturated','sample_seen',
           'last_read_accepted','decode_matches_sample')
    report=dict(zip(names,struct.unpack_from('<8B',blob,16)))
    report['setup']=dict(zip(('status','shutdown','ready'),struct.unpack_from('<3B',blob,24)))
    report['sample'],report['decoded']=sample(blob,28),decoded(blob,48)
    report.update(zip(('captured_samples','not_due','missed_releases'),struct.unpack_from('<3I',blob,76)))
    for name,offset in (('setup_timing',88),('read_timing',108),('poll_timing',128)):
        report[name]=timing(blob,offset)
    count=report['captured_samples']
    if count>128: return report,None
    captures=[]
    for index in range(count):
        offset=148+76*index
        value={'sample':sample(blob,offset),'decoded':decoded(blob,offset+20)}
        value.update(zip(('call_started_us','call_returned_us','poll_closed_us','source_us',
                          'read_us','poll_us','missed_before'),struct.unpack_from('<7I',blob,offset+48)))
        captures.append(value)
    return report,captures


def domains(report,captures):
    errors=[]
    def check(ok,where):
        if not ok: errors.append(where)
    for name in ('fresh','clock_fault','counter_saturated','sample_seen','last_read_accepted','decode_matches_sample'):
        check(report[name] in (0,1),'report.'+name)
    check(report['phase'] in range(5),'report.phase')
    check(report['fault'] in range(8),'report.fault')
    for name,domain in (('status',range(15)),('shutdown',range(3)),('ready',(0,1))):
        check(report['setup'][name] in domain,'report.setup.'+name)
    items=[('report',report)]+[(f'captures[{i}]',value) for i,value in enumerate(captures or [])]
    for path,value in items:
        for name,domain in (('status',range(15)),('shutdown',range(3)),('valid',(0,1))):
            check(value['sample'][name] in domain,path+'.sample.'+name)
        d=value['decoded'];e=d['evidence']
        check(d['qualification'] in range(6),path+'.decoded.qualification')
        for name,domain in (('explicit_values',(0,1)),('contract_valid',(0,1)),('presence',(1,2,3)),('level',range(4))):
            check(e[name] in domain,path+'.decoded.evidence.'+name)
    return errors


def timing_errors(report):
    errors=[]
    for name in ('setup_timing','read_timing','poll_timing'):
        t=report[name]
        valid=t['last_valid'] in (0,1) and t['measured_calls']<=t['calls']
        valid &= t['last_us']<=t['maximum_us']<HALF
        valid &= not t['last_valid'] or t['measured_calls']>0
        valid &= t['measured_calls']>0 or (t['last_us'],t['maximum_us'],t['last_valid'])==(0,0,0)
        if not valid: errors.append('report.'+name)
    return errors


def capture_errors(captures):
    errors=[]
    for index,c in enumerate(captures):
        s=c['sample'];d=c['decoded'];e=d['evidence'];start=c['call_started_us']
        ordered=[(value-start)&MASK for value in (s['started_us'],s['completed_us'],c['call_returned_us'],c['poll_closed_us'])]
        if ordered!=sorted(ordered) or ordered[-1]>=HALF: errors.append(f'capture{index}:chronology')
        if (s['status'],s['shutdown'],s['valid'],s['sequence'])!=(0,0,1,index+1) or s['raw']>16383:
            errors.append(f'capture{index}:source shape')
        source=(s['completed_us']-s['started_us'])&MASK
        if source>=100 or c['source_us']!=source: errors.append(f'capture{index}:source duration')
        if c['read_us']!=ordered[2] or c['poll_us']!=ordered[3]: errors.append(f'capture{index}:wrapper duration')
        if (d['qualification'],e['explicit_values'],e['contract_valid'],e['presence'],e['level'],d['candidate_mask'])!=(2,1,1,3,0,0):
            errors.append(f'capture{index}:decode shape')
        if any(e[name]!=s[name] for name in ('raw','sequence','started_us','completed_us')):
            errors.append(f'capture{index}:decode source')
        if index==0:
            if c['missed_before']: errors.append('capture0:first missed')
        else:
            previous=captures[index-1]
            age=(start-previous['sample']['started_us'])&MASK
            if not 1000<=age<HALF or c['missed_before']!=age//1000-1:
                errors.append(f'capture{index}:cadence')
            if ((start-previous['poll_closed_us'])&MASK)>=HALF: errors.append(f'capture{index}:order')
    return errors


def consistency(report,captures):
    errors=domains(report,captures)+timing_errors(report)
    if captures is None: return errors+['report.captured_samples outside capacity']
    errors+=capture_errors(captures)
    phase,fault,count=report['phase'],report['fault'],report['captured_samples']
    if phase==3: valid=(fault==0 and count==128)
    elif phase==4: valid=(fault!=0 and count<128)
    else: valid=(fault==0 and count<128 and (phase not in (0,1) or count==0))
    if not valid: errors.append('phase/fault/count relationship')
    if report['clock_fault'] and phase!=4 or fault==7 and not report['clock_fault']:
        errors.append('clock fault relationship')
    missed=min(MASK,sum(c['missed_before'] for c in captures))
    if report['missed_releases']<missed: errors.append('missed_releases below committed sum')
    if phase!=3 or count!=128: return errors
    if report['setup']!={'status':0,'shutdown':0,'ready':1}: errors.append('complete setup')
    if any(report[name]!=1 for name in ('sample_seen','last_read_accepted','decode_matches_sample')) or report['clock_fault']:
        errors.append('complete accepted flags')
    if any(report[name]!=captures[-1][name] for name in ('sample','decoded')):
        errors.append('complete latest semantic identity')
    t=report['setup_timing']
    if (t['calls'],t['measured_calls'],t['last_valid'])!=(1,1,1): errors.append('complete setup counts')
    for prefix,calls in (('read',128),('poll',min(MASK,128+report['not_due']))):
        t=report[prefix+'_timing'];durations=[c[prefix+'_us'] for c in captures]
        if (t['calls'],t['measured_calls'],t['last_valid'],t['last_us'],t['maximum_us'])!=(calls,128,1,durations[-1],max(durations)):
            errors.append('complete '+prefix+' timing')
    if report['missed_releases']!=missed: errors.append('complete missed sum')
    return errors


def stats(values):
    return None if not values else {'count':len(values),'minimum':min(values),'maximum':max(values),
                                    'mean':statistics.mean(values),'median':statistics.median(values)}


def summarize(report,captures):
    result={'phase':PHASES[report['phase']] if report['phase']<5 else 'UNKNOWN',
            'fault':FAULTS[report['fault']] if report['fault']<8 else 'UNKNOWN',
            'setup_status':STATUS[report['setup']['status']] if report['setup']['status']<15 else 'UNKNOWN',
            'report':report,'committed_statistics':None}
    if captures is None: return result
    counters={}
    for c in captures:
        q=c['decoded']['qualification'];name=QUALIFICATIONS[q] if q<len(QUALIFICATIONS) else str(q)
        counters[name]=counters.get(name,0)+1
    result['committed_statistics']={'raw':stats([c['sample']['raw'] for c in captures]),
        'source_us':stats([c['source_us'] for c in captures]),'read_us':stats([c['read_us'] for c in captures]),
        'poll_us':stats([c['poll_us'] for c in captures]),'decode_qualification_counts':counters,
        'first':captures[0] if captures else None,'last':captures[-1] if captures else None,
        'first_S_to_last_C_us':((captures[-1]['poll_closed_us']-captures[0]['call_started_us'])&MASK) if captures else None}
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--first',required=True,type=Path)
    parser.add_argument('--second',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    blobs=[args.first.read_bytes(),args.second.read_bytes()]
    snapshots=[]
    for path,blob in zip((args.first,args.second),blobs):
        report,captures=unpack(blob)
        errors=consistency(report,captures)
        snapshots.append({'file':str(path),'bytes':len(blob),'sha256':hashlib.sha256(blob).hexdigest(),
                          'errors':errors,'valid':not errors,'summary':summarize(report,captures),'captures':captures})
    stable=blobs[0]==blobs[1]
    terminal=all(s['summary']['phase'] in ('COMPLETE','FAULT') for s in snapshots)
    result={'independent_schema_decode':True,'byte_identical':stable,'snapshots':snapshots,
            'frozen_terminal':stable and terminal and all(s['valid'] for s in snapshots),
            'physical_acceptance':False,'analysis_source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    with args.output.open('x',encoding='utf-8') as output: json.dump(result,output,indent=2);output.write('\n')
    print(json.dumps({key:value for key,value in result.items() if key!='snapshots'}))
    for snapshot in snapshots: print(json.dumps({'valid':snapshot['valid'],'errors':snapshot['errors'],'summary':snapshot['summary']},indent=2))


if __name__=='__main__':
    main()
