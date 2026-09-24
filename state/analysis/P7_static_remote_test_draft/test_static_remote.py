# Independently tests remote action schemas through real Linux descriptor fixtures.
# Uses actual nonroot ownership and fixed source/validator bytes without transport.
# Execute only after freeze_remote.json and an explicit coordinator host-test GO.
import base64
import contextlib
import copy
import errno
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import socket
import stat
import subprocess
import sys
import tempfile
import types
import unittest
from unittest import mock
try:
    import pwd
except ImportError:
    pwd = None

ROOT=Path(__file__).resolve().parents[3]
DRAFT=Path(__file__).resolve().parent
RAW=ROOT/'state/analysis/P7_static_link_probe_raw'


def load(path,name):
    module=types.ModuleType(name)
    module.__file__=str(path)
    sys.modules[name]=module
    exec(compile(path.read_bytes(),str(path),'exec'),module.__dict__)
    return module


@unittest.skipUnless(sys.platform.startswith('linux'),'Actual Linux descriptor fixtures required')
class StaticRemoteContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if os.geteuid()==0:
            raise RuntimeError('Run helper tests under the actual nonroot WSL account')
        freeze=json.loads((DRAFT/'freeze_remote.json').read_text())
        if freeze.get('status')!='FROZEN_FOR_AUTHORIZED_HOST_TEST':
            raise RuntimeError('Remote tests have not been frozen')
        for relative,expected in freeze['inputs_sha256'].items():
            if hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()!=expected:
                raise RuntimeError('Frozen helper input changed: '+relative)
        cls.f=load(ROOT/'state/analysis/P7_static_runner_test_draft/public_fixtures.py','remote_public_fixtures')
        cls.module=load(RAW/'static_remote.py','independent_static_remote_under_test')
        raw,cls.source_bytes,cls.source_report=cls.f.source_packet()
        cls.m=cls.f.packed(raw)
        validator=(RAW/'static_artifacts.py').read_bytes()
        if cls.f.digest(validator)!=cls.f.VALIDATOR_SHA:raise RuntimeError('Validator changed')
        cls.v=cls.f.packed(validator)
        cls.packet,cls.report=cls.f.artifact_packet()

    def setUp(self):
        self.temporary=tempfile.TemporaryDirectory(prefix='sumox_remote_',dir='/dev/shm')
        self.addCleanup(self.temporary.cleanup)
        self.root=Path(self.temporary.name)
        self.logical(self.f.R).mkdir(parents=True,mode=0o700)
        self.logical('/tmp').mkdir()
        self.logical('/proc/sys/kernel/random').mkdir(parents=True)
        self.logical('/proc/sys/kernel/random/boot_id').write_text(self.f.BOOT_ID+'\n')
        self.logical('/proc/meminfo').write_text('MemTotal: 1048576 kB\nMemAvailable: 524288 kB\n')
        self.machine='aarch64'
        self.available_blocks=262144
        self.account_name='arduino'
        self.claim=None

    def logical(self,path):
        return self.root/path.lstrip('/')

    def invoke(self,argv):
        output,errors=io.StringIO(),io.StringIO()
        account=pwd.struct_passwd((self.account_name,'x',os.geteuid(),os.getegid(),
                                  'Synthetic account','/home/arduino','/bin/sh'))
        uname=os.uname_result(('Linux','fixture','synthetic-kernel','fixture',self.machine))
        vfs=os.statvfs_result((4096,4096,300000,self.available_blocks,self.available_blocks,1000,1000,1000,0,255))
        def named(name):
            if name!='arduino':raise KeyError(name)
            return account
        with mock.patch.object(pwd,'getpwuid',return_value=account),mock.patch.object(pwd,'getpwnam',side_effect=named), \
             mock.patch.object(os,'uname',return_value=uname),mock.patch.object(os,'statvfs',return_value=vfs), \
             mock.patch.object(os,'fstatvfs',return_value=vfs), \
             mock.patch.object(platform,'system',return_value='Linux'), \
             mock.patch.object(platform,'machine',return_value=self.machine), \
             mock.patch.object(platform,'release',return_value='synthetic-kernel'), \
             mock.patch.object(socket,'socket',side_effect=AssertionError('No network from helper')), \
             mock.patch.object(subprocess,'Popen',side_effect=AssertionError('No processes from helper')), \
             contextlib.redirect_stdout(output),contextlib.redirect_stderr(errors):
            code=self.module.main(argv,fs_root=self.root)
        text=output.getvalue()
        self.assertTrue(text.endswith('\n'))
        self.assertEqual(len(text.splitlines()),1)
        data=json.loads(text)
        self.assertEqual(set(data),{'schema','action','run_id','ok','data','error'})
        self.assertEqual(data['schema'],'static-remote-v1')
        if code==0:
            self.assertIs(data['ok'],True)
            self.assertIsNone(data['error'])
            self.assertEqual(errors.getvalue(),'')
        else:
            self.assertIn(code,(2,3))
            self.assertIs(data['ok'],False)
            self.assertEqual(set(data['error']),{'code','message'})
        return code,data

    def action(self,action,*arguments):
        code,data=self.invoke([action,self.f.RUN,*arguments])
        self.assertEqual((data['action'],data['run_id']),(action,self.f.RUN))
        return code,data

    def succeed(self,action,*arguments):
        code,data=self.action(action,*arguments)
        self.assertEqual(code,0,data)
        return data['data']

    def rejected(self,action,*arguments,code=None):
        status,data=self.action(action,*arguments)
        self.assertEqual(status,2,data)
        if code:self.assertEqual(data['error']['code'],code)
        return data['data']

    def make_claim(self):
        result=self.succeed('claim')
        self.claim=result['claim']
        return self.f.canonical(self.claim)

    def materialize_source(self):
        source=self.logical(self.f.S)
        source.mkdir(parents=True,exist_ok=True)
        for name,raw in self.source_bytes.items():
            path=source/name
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(raw)

    def materialize_artifacts(self):
        _,build,artifacts=self.f.paths()
        for name,data in self.packet.items():
            (self.logical(build)/name).write_bytes(data)
        (self.logical(artifacts)/'app.ino.bin-zsk.bin').write_bytes(self.packet['app.ino.bin-zsk.bin'])

    def add_process(self,pid,argv,exe='/usr/bin/python3',state='S',kernel=0):
        folder=self.logical('/proc')/str(pid)
        folder.mkdir()
        (folder/'cmdline').write_bytes(b'\0'.join(word.encode() for word in argv)+(b'\0' if argv else b''))
        (folder/'comm').write_text(Path(exe.removesuffix(' (deleted)')).name+'\n')
        (folder/'status').write_text(f'Name:\tfixture\nState:\t{state} (fixture)\nKthread:\t{kernel}\n')
        (folder/'exe').symlink_to(exe)
        return folder

    def test_inventory_uses_real_uid_with_fake_account_and_exact_resource_thresholds(self):
        result=self.succeed('inventory')
        self.assertEqual(set(result),{'identity','resources','compiler_candidates'})
        expected=self.f.identity()
        expected.update(uid=os.geteuid(),gid=os.getegid(),python=list(sys.version_info[:3]))
        self.assertEqual(result['identity'],expected)
        self.assertEqual(result['resources'],self.f.resources())
        self.assertEqual(result['compiler_candidates'],[])

    def test_invalid_action_run_and_arguments_do_not_mutate_filesystem(self):
        cases=[[],['unknown',self.f.RUN],['claim','A'*32],['claim',self.f.RUN,'extra'],
               ['read',self.f.RUN],['inventory',self.f.RUN,'extra'],['claim',self.f.RUN+'0']]
        for argv in cases:
            with self.subTest(argv=argv),mock.patch.object(os,'mkdir',side_effect=AssertionError('Mutation before admission')):
                code,data=self.invoke(argv)
            self.assertEqual(code,2)
            self.assertEqual(data['error']['code'],'BAD_REQUEST')
            self.assertEqual(data['data'],{})

    def test_inventory_identity_resource_and_missing_observation_rejections(self):
        self.machine='x86_64'
        self.rejected('inventory',code='IDENTITY')
        self.machine='aarch64'
        self.available_blocks=262143
        self.rejected('inventory',code='RESOURCE_MINIMUM')
        self.available_blocks=262144
        self.logical('/proc/meminfo').write_text('MemAvailable: 524287 kB\n')
        self.rejected('inventory',code='RESOURCE_MINIMUM')
        self.logical('/proc/meminfo').write_text('MemTotal: 999999 kB\n')
        self.rejected('inventory')

    def test_process_detector_ignores_argument_text_and_excludes_kernel_zombie(self):
        self.add_process(40,['/usr/bin/python3','-c','gcc arduino-cli compile arm-zephyr-eabi-ld'])
        self.add_process(41,[],state='S',kernel=1)
        self.add_process(42,[],state='Z',kernel=0)
        self.assertEqual(self.succeed('inventory')['compiler_candidates'],[])

    def test_process_candidates_are_basename_based_sorted_and_reasons_exact(self):
        self.add_process(81,['/usr/bin/arduino-cli','--config-file','x','compile'],exe='/usr/bin/arduino-cli')
        self.add_process(12,['/tools/arm-zephyr-eabi-g++','source.cpp'],exe='/tools/arm-zephyr-eabi-g++ (deleted)')
        data=self.rejected('inventory',code='COMPILER_PRESENT')
        self.assertEqual([item['pid'] for item in data['compiler_candidates']],[12,81])
        self.assertEqual([item['reason'] for item in data['compiler_candidates']],['compiler executable','arduino-cli compile'])
        self.assertTrue(all(set(item)=={'pid','comm','argv0','reason'} for item in data['compiler_candidates']))

    def test_process_incomplete_malformed_and_bounded_records_fail(self):
        folder=self.add_process(51,['/usr/bin/python3'])
        cases=[('cmdline',b'/usr/bin/python3'),('cmdline',b'\xff\0'),('cmdline',b'x'*65537),
               ('status',b'State: S\n'),('status',b'State: S\nState: S\nKthread: 0\n'),
               ('cmdline',b'')]
        for name,content in cases:
            path=folder/name
            original=path.read_bytes()
            path.write_bytes(content)
            with self.subTest(name=name,length=len(content)):
                self.rejected('inventory',code='PROCESS_INSPECTION')
            path.write_bytes(original)

    def test_unreadable_exe_optional_only_with_complete_cmdline_and_comm(self):
        self.add_process(60,['/usr/bin/python3'])
        original=os.readlink
        def denied(path,*args,**kwargs):
            if os.fspath(path).endswith('exe'):raise PermissionError(errno.EACCES,'synthetic exe denied')
            return original(path,*args,**kwargs)
        with mock.patch.object(os,'readlink',denied):
            self.assertEqual(self.succeed('inventory')['compiler_candidates'],[])
        self.logical('/proc/60/comm').unlink()
        with mock.patch.object(os,'readlink',denied):
            # A completely vanished process is permitted; incomplete surviving files are not.
            self.rejected('inventory',code='PROCESS_INSPECTION')

    def test_source_exact_stage_bytes_and_empty_directories_are_read_only(self):
        self.materialize_source()
        self.logical(self.f.S+'/empty/subdir').mkdir(parents=True)
        result=self.succeed('source',self.m)
        self.assertEqual(result,self.source_report)
        for name,expected in self.source_bytes.items():
            self.assertEqual((self.logical(self.f.S)/name).read_bytes(),expected)

    def test_source_extra_missing_changed_and_symlink_rejected(self):
        self.materialize_source()
        target=self.logical(self.f.S+'/app.ino')
        original=target.read_bytes()
        target.write_bytes(original+b'changed')
        self.rejected('source',self.m,code='SOURCE_DRIFT')
        target.unlink()
        self.rejected('source',self.m,code='SOURCE_SET')
        target.write_bytes(original)
        extra=self.logical(self.f.S+'/unexpected.txt')
        extra.write_bytes(b'x')
        self.rejected('source',self.m,code='SOURCE_SET')
        extra.unlink()
        target.unlink()
        target.symlink_to('/outside/never-follow')
        self.rejected('source',self.m)

    def test_source_manifest_pin_and_compression_cannot_be_redefined(self):
        for encoded in (self.m+'\n',self.m[:-1],self.f.packed(b'{}'),
                        base64.b64encode(b'not-zlib').decode(),self.f.packed(b'x'*65537)):
            self.rejected('source',encoded,code='BAD_REQUEST')

    def test_source_symlink_ancestry_is_not_followed(self):
        self.logical(self.f.R+'/'+self.f.SOURCE).symlink_to('/outside/never-follow')
        self.rejected('source',self.m,code='PATH')

    def test_source_fifo_rejection_is_nonblocking(self):
        self.materialize_source()
        target=self.logical(self.f.S+'/app.ino')
        target.unlink()
        os.mkfifo(target)
        original=os.open
        def no_hang(path,flags,*args,**kwargs):
            if Path(os.fsdecode(path)).name=='app.ino' and not flags&os.O_NONBLOCK:
                raise AssertionError('Source FIFO must not block before type checking')
            return original(path,flags,*args,**kwargs)
        with mock.patch.object(os,'open',no_hang):self.rejected('source',self.m)

    def test_claim_creation_order_modes_real_identities_and_exclusive_reentry(self):
        result=self.succeed('claim')
        u,b,a=self.f.paths()
        expected=[self.f.R+'/_app_builds',self.f.R+'/_app_builds/static-app-probe-v1',
                  self.f.R+'/_app_builds/static-app-probe-v1/'+self.f.SOURCE,
                  str(Path(u).parent),u,b,a]
        self.assertEqual(result['created'],expected)
        self.assertEqual(set(result),{'claim','created'})
        self.assertEqual(result['claim']['boot_id'],self.f.BOOT_ID)
        for key,path in (('run',u),('build',b),('artifacts',a)):
            info=self.logical(path).stat()
            self.assertEqual(result['claim']['directories'][key],dict(device=info.st_dev,inode=info.st_ino))
            self.assertEqual(info.st_uid,os.geteuid())
            self.assertEqual(stat.S_IMODE(info.st_mode),0o700)
        self.rejected('claim',code='CLAIM_EXISTS')

    def test_existing_run_entry_and_symlink_parent_cannot_be_reused(self):
        u,_,_=self.f.paths()
        self.logical(str(Path(u).parent)).mkdir(parents=True)
        self.logical(u).symlink_to('/missing/never-follow')
        self.rejected('claim',code='CLAIM_EXISTS')

    def test_partial_claim_keeps_successful_directories_without_rollback(self):
        original=os.mkdir
        def fail_artifacts(path,*args,**kwargs):
            if Path(os.fsdecode(path)).name=='artifacts':raise OSError(errno.ENOSPC,'synthetic mkdir failure')
            return original(path,*args,**kwargs)
        with mock.patch.object(os,'mkdir',fail_artifacts):
            result=self.rejected('claim',code='CLAIM_INCOMPLETE')
        self.assertIsNone(result['claim'])
        u,b,a=self.f.paths()
        self.assertTrue(self.logical(u).is_dir())
        self.assertTrue(self.logical(b).is_dir())
        self.assertFalse(self.logical(a).exists())
        self.assertIsNone(result['partial_directories']['artifacts'])
        self.assertEqual(result['created'][-2:],[u,b])
        self.rejected('claim',code='CLAIM_EXISTS')

    def test_invalid_boot_after_last_mkdir_preserves_all_partial_directory_ids(self):
        original=os.mkdir
        changed=[False]
        def corrupt_boot(path,*args,**kwargs):
            result=original(path,*args,**kwargs)
            if Path(os.fsdecode(path)).name=='artifacts':
                changed[0]=True
                self.logical('/proc/sys/kernel/random/boot_id').write_bytes(b'\xff\n')
            return result
        with mock.patch.object(os,'mkdir',corrupt_boot):
            result=self.rejected('claim',code='CLAIM_INCOMPLETE')
        self.assertTrue(changed[0])
        u,b,a=self.f.paths()
        self.assertEqual(result['created'][-3:],[u,b,a])
        for key,path in (('run',u),('build',b),('artifacts',a)):
            info=self.logical(path).stat()
            self.assertEqual(result['partial_directories'][key],dict(device=info.st_dev,inode=info.st_ino))

    def test_absent_all_eight_and_any_entry_including_dangling_links_fails(self):
        handle=self.make_claim()
        empty=self.succeed('absent',handle)
        self.assertEqual(set(empty['outputs']),set(self.f.file_records(self.packet)))
        self.assertTrue(all(value=='absent' for value in empty['outputs'].values()))
        u,_,_=self.f.paths()
        for name in empty['outputs']:
            target=self.logical(u+'/'+name)
            target.symlink_to('/missing/never-follow')
            result=self.rejected('absent',handle,code='OUTPUT_PRESENT')
            self.assertEqual(result['outputs'][name],'present')
            target.unlink()

    def test_claim_handle_boot_and_directory_replacement_fail(self):
        handle=self.make_claim()
        changed=copy.deepcopy(self.claim)
        changed['directories']['build']['inode']+=1
        self.rejected('absent',self.f.canonical(changed),code='PATH')
        self.logical('/proc/sys/kernel/random/boot_id').write_text('aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee\n')
        self.rejected('absent',handle,code='PATH')

    def test_claim_handle_noncanonical_or_extra_fields_rejected(self):
        self.make_claim()
        pretty=base64.b64encode(json.dumps(self.claim,indent=2).encode()).decode()
        changed=copy.deepcopy(self.claim)
        changed['extra']=True
        duplicate=json.dumps(self.claim)[:-1]+',"run_id":"'+self.f.RUN+'"}'
        for value in (pretty,self.f.canonical(changed),self.f.canonical(self.claim)+'\n',
                      base64.b64encode(duplicate.encode()).decode()):
            self.rejected('absent',value,code='BAD_REQUEST')

    def test_artifacts_and_layout_use_real_unchanged_validator(self):
        handle=self.make_claim()
        self.materialize_artifacts()
        observation=self.succeed('artifacts',handle)
        self.assertEqual(len(observation['files']),8)
        u,_,_=self.f.paths()
        for name,record in observation['files'].items():
            info=self.logical(u+'/'+name).stat()
            self.assertEqual(record['identity'],dict(device=info.st_dev,inode=info.st_ino,bytes=info.st_size,
                                                      mtime_ns=info.st_mtime_ns,ctime_ns=info.st_ctime_ns))
            self.assertEqual(record['sha256'],self.f.digest(self.logical(u+'/'+name).read_bytes()))
        layout=self.succeed('layout',handle,self.v)
        self.assertEqual(layout['report'],self.report)
        self.assertEqual(layout['files'],observation['files'])
        self.assertEqual(layout['validator_sha256'],self.f.VALIDATOR_SHA)

    def test_artifact_missing_empty_oversize_directory_and_fifo_all_observed(self):
        handle=self.make_claim()
        self.materialize_artifacts()
        _,build,_=self.f.paths()
        base=self.logical(build)
        (base/'app.ino.elf').unlink()
        (base/'app.ino_debug.elf').write_bytes(b'')
        with (base/'app.ino_temp.elf').open('wb') as output:output.truncate(16777217)
        (base/'app.ino.map').unlink()
        (base/'app.ino.map').mkdir()
        (base/'app.ino.bin').unlink()
        os.mkfifo(base/'app.ino.bin')
        original=os.open
        def no_hang(path,flags,*args,**kwargs):
            if Path(os.fsdecode(path)).name=='app.ino.bin' and not flags&os.O_NONBLOCK:
                raise AssertionError('FIFO must be opened nonblocking before fstat')
            return original(path,flags,*args,**kwargs)
        with mock.patch.object(os,'open',no_hang):
            result=self.rejected('artifacts',handle,code='ARTIFACT_SET')
        expected={'app.ino.elf':'missing','app.ino_debug.elf':'empty','app.ino_temp.elf':'oversize',
                  'app.ino.map':'nonregular','app.ino.bin':'nonregular'}
        self.assertEqual(len(result['files']),8)
        for name,state in expected.items():
            record=result['files']['build/'+name]
            self.assertEqual(record['state'],state)
            self.assertIsNone(record['sha256'])
            if state in ('missing','nonregular'):self.assertIsNone(record['identity'])

    def test_export_mismatch_and_invalid_layout_are_not_success(self):
        handle=self.make_claim()
        self.materialize_artifacts()
        _,build,export=self.f.paths()
        self.logical(export+'/app.ino.bin-zsk.bin').write_bytes(b'changed')
        self.rejected('artifacts',handle,code='ARTIFACT_SET')
        self.logical(export+'/app.ino.bin-zsk.bin').write_bytes(self.packet['app.ino.bin-zsk.bin'])
        data=bytearray(self.packet['app.ino.elf'])
        data[4]=2
        self.logical(build+'/app.ino.elf').write_bytes(data)
        result=self.rejected('layout',handle,self.v,code='LAYOUT_REJECTED')
        self.assertIsNone(result['report'])

    def replace_during_fstat(self,target,contents):
        original=os.fstat
        fired=[False]
        def observed(fd):
            info=original(fd)
            if not fired[0]:
                try:current=os.readlink('/proc/self/fd/'+str(fd))
                except OSError:current=''
                if current==str(target):
                    fired[0]=True
                    replacement=target.with_name(target.name+'.replacement')
                    replacement.write_bytes(contents)
                    os.replace(replacement,target)
            return info
        return fired,observed

    def test_artifact_identical_byte_replacement_is_unstable_not_hash_success(self):
        handle=self.make_claim()
        self.materialize_artifacts()
        _,build,_=self.f.paths()
        target=self.logical(build+'/app.ino.elf')
        initial=target.stat()
        fired,observed=self.replace_during_fstat(target,self.packet['app.ino.elf'])
        with mock.patch.object(os,'fstat',observed):
            result=self.rejected('artifacts',handle,code='ARTIFACT_SET')
        self.assertTrue(fired[0])
        record=result['files']['build/app.ino.elf']
        self.assertEqual(record['state'],'unstable')
        self.assertEqual(record['identity']['inode'],initial.st_ino)
        self.assertIsNone(record['sha256'])

    def test_source_identical_byte_inode_replacement_cannot_pass_hash_only_check(self):
        self.materialize_source()
        target=self.logical(self.f.S+'/app.ino')
        fired,observed=self.replace_during_fstat(target,self.source_bytes['app.ino'])
        with mock.patch.object(os,'fstat',observed):
            self.rejected('source',self.m,code='SOURCE_DRIFT')
        self.assertTrue(fired[0])

    def test_validator_bytes_cannot_be_replaced_even_with_valid_artifacts(self):
        handle=self.make_claim()
        self.materialize_artifacts()
        self.rejected('layout',handle,self.f.packed(b'def validate_artifacts(x): return {}'),code='BAD_REQUEST')
        self.rejected('layout',handle,self.f.packed(b'x'*32769),code='BAD_REQUEST')

    def test_read_final_only_exact_range_hash_and_canonical_content(self):
        handle=self.make_claim()
        self.materialize_artifacts()
        elf=self.packet['app.ino.elf']
        result=self.succeed('read',handle,'app.ino.elf','0',str(len(elf)),self.f.digest(elf))
        self.assertEqual((result['name'],result['offset'],result['length']),('app.ino.elf',0,len(elf)))
        self.assertEqual(base64.b64decode(result['base64'],validate=True),elf)
        self.assertEqual(result['chunk_sha256'],self.f.digest(elf))
        cases=[('app.ino_debug.elf','0',str(len(elf)),self.f.digest(elf)),
               ('../app.ino.elf','0',str(len(elf)),self.f.digest(elf)),
               ('app.ino.elf','00',str(len(elf)),self.f.digest(elf)),
               ('app.ino.elf','-1',str(len(elf)),self.f.digest(elf)),
               ('app.ino.elf','1',str(len(elf)),self.f.digest(elf)),
               ('app.ino.elf','262144','1',self.f.digest(elf)),
               ('app.ino.elf','0',str(len(elf)-1),self.f.digest(elf)),
               ('app.ino.elf','0',str(len(elf)),'0'*64)]
        for arguments in cases:
            with self.subTest(arguments=arguments):self.rejected('read',handle,*arguments)

    def test_postcheck_preserves_independent_failures_and_ignores_resource_floor(self):
        self.materialize_source()
        handle=self.make_claim()
        self.materialize_artifacts()
        self.available_blocks=1
        self.logical('/proc/meminfo').write_text('MemAvailable: 1 kB\n')
        self.assertEqual(self.succeed('postcheck',handle,self.m)['resources']['available_ram_bytes'],1024)
        self.machine='x86_64'
        self.logical(self.f.S+'/app.ino').write_bytes(b'drift')
        _,build,_=self.f.paths()
        self.logical(build+'/app.ino.map').unlink()
        result=self.rejected('postcheck',handle,self.m,code='POSTCHECK_FAILED')
        self.assertEqual([failure['check'] for failure in result['failures']],['identity','source','files'])
        self.assertIsNotNone(result['resources'])
        self.assertEqual(result['files']['build/app.ino.map']['state'],'missing')

    def test_failed_claim_blocks_outputs_but_not_unrelated_postchecks(self):
        self.materialize_source()
        self.make_claim()
        altered=copy.deepcopy(self.claim)
        altered['directories']['build']['inode']+=1
        result=self.rejected('postcheck',self.f.canonical(altered),self.m,code='POSTCHECK_FAILED')
        self.assertEqual([failure['check'] for failure in result['failures']],['claim','files'])
        self.assertEqual(result['source'],self.source_report)
        self.assertIsNone(result['files'])


if __name__=='__main__':unittest.main(verbosity=2)
