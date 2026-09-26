EXPECTED={'boot_id': '55c386b9-fe6d-4388-a7f4-1d91e0bb49d8', 'gid': 1000, 'home': '/home/arduino', 'machine': 'aarch64', 'python': [3, 13, 5], 'release': '6.16.7-g0dd6551ae96b', 'sysname': 'Linux', 'uid': 1000, 'user': 'arduino'}
PINS=[{'path': '/home/arduino/sumox26_codex_build/app-motor-const-4bc3a2e6-run01-upload/upload_result.json', 'bytes': 1903, 'sha256': 'c0e9d53fb5171e58412eb4515e63b1dbb0068d6a81fe5a9e68e587bcc8496a02'}, {'path': '/home/arduino/sumox26_codex_build/app-motor-const-4bc3a2e6-run01-capture/capture_result.json', 'bytes': 7100, 'sha256': '9b879b418ad996a371e184b107b29617ce8cad0c189b7bbbb1427e34f80a1fd0'}, {'path': '/home/arduino/sumox26_codex_build/app-motor-const-4bc3a2e6-run01-capture/07-first.trace.bin', 'bytes': 2128, 'sha256': '4d0b02805f5442e1ff13e49788e8b5c3c1bc187d4017362619c349eeb0e1386e'}, {'path': '/home/arduino/sumox26_codex_build/app-motor-const-4bc3a2e6-run01-capture/08-first.report.bin', 'bytes': 1168, 'sha256': '036bedcf262e13f3f9863b244832ee7bc60a0c8400821f957c57630dd25f3f9d'}, {'path': '/home/arduino/sumox26_codex_build/app-motor-const-4bc3a2e6-run01-capture/09-first.runtime.bin', 'bytes': 600, 'sha256': '90fe58fa81ac28d8e71f6e1a5735d88d7abb616e9af8b6c433d62b6a7172e8f4'}, {'path': '/home/arduino/sumox26_codex_build/app-motor-const-4bc3a2e6-run01-capture/10-first.transaction.bin', 'bytes': 504, 'sha256': '140c4fb57b89069864d119135812a14312ca52780d4375fd50c852151e3c67bd'}, {'path': '/home/arduino/sumox26_codex_build/app-motor-const-4bc3a2e6-run01-capture/11-first.settle.bin', 'bytes': 28, 'sha256': '8630eb32a862922c03f5838a966758ddcbd8817966be05139ec748581e0787d5'}, {'path': '/home/arduino/sumox26_codex_build/app-motor-const-4bc3a2e6-run01-capture/12-first.gate.bin', 'bytes': 88, 'sha256': 'd6ae3cfc721075c591b6afb0dd1de3a58632921e9c743d0f845d971b75592e1f'}, {'path': '/home/arduino/sumox26_codex_build/app-motor-const-4bc3a2e6-run01-capture/13-second.trace.bin', 'bytes': 2128, 'sha256': '4d0b02805f5442e1ff13e49788e8b5c3c1bc187d4017362619c349eeb0e1386e'}, {'path': '/home/arduino/sumox26_codex_build/app-motor-const-4bc3a2e6-run01-capture/14-second.report.bin', 'bytes': 1168, 'sha256': '036bedcf262e13f3f9863b244832ee7bc60a0c8400821f957c57630dd25f3f9d'}, {'path': '/home/arduino/sumox26_codex_build/app-motor-const-4bc3a2e6-run01-capture/15-second.runtime.bin', 'bytes': 600, 'sha256': '90fe58fa81ac28d8e71f6e1a5735d88d7abb616e9af8b6c433d62b6a7172e8f4'}, {'path': '/home/arduino/sumox26_codex_build/app-motor-const-4bc3a2e6-run01-capture/16-second.transaction.bin', 'bytes': 504, 'sha256': '140c4fb57b89069864d119135812a14312ca52780d4375fd50c852151e3c67bd'}, {'path': '/home/arduino/sumox26_codex_build/app-motor-const-4bc3a2e6-run01-capture/17-second.settle.bin', 'bytes': 28, 'sha256': '8630eb32a862922c03f5838a966758ddcbd8817966be05139ec748581e0787d5'}, {'path': '/home/arduino/sumox26_codex_build/app-motor-const-4bc3a2e6-run01-capture/18-second.gate.bin', 'bytes': 88, 'sha256': 'd6ae3cfc721075c591b6afb0dd1de3a58632921e9c743d0f845d971b75592e1f'}]
import base64,zlib,hashlib,json,os,sys,types,signal
signal.alarm(60)
source=zlib.decompress(base64.b64decode(sys.argv[1],validate=True))
if hashlib.sha256(source).hexdigest()!='8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8':raise ValueError('Helper changed')
h=types.ModuleType('read_only_result_helper');h.__file__='/__sumox__/static_remote.py';exec(compile(source,h.__file__,'exec'),h.__dict__)
fd=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
try:
 before=h.identity(fd)
 if before!=EXPECTED:raise ValueError('Identity changed')
 rows=[]
 for pin in PINS:
  body=h.logical_read(fd,pin['path'],pin['bytes'])
  if len(body)!=pin['bytes'] or hashlib.sha256(body).hexdigest()!=pin['sha256']:raise ValueError('Result pin mismatch')
  rows.append(dict(pin,data_base64=base64.b64encode(body).decode('ascii')))
 for pin in PINS:
  body=h.logical_read(fd,pin['path'],pin['bytes'])
  if len(body)!=pin['bytes'] or hashlib.sha256(body).hexdigest()!=pin['sha256']:raise ValueError('Closing result pin mismatch')
 after=h.identity(fd)
 if after!=before:raise ValueError('Closing identity changed')
 print(json.dumps({'status':'FILE_ONLY_RESULTS_VERIFIED','identity_before':before,'identity_after':after,'files':rows,'closing_file_checks':len(PINS)},separators=(',',':')))
finally:os.close(fd)
