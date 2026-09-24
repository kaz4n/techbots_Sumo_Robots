import hashlib, json, pathlib, shutil
work = pathlib.Path('/dev/shm/sumox_d120_configured')
out = pathlib.Path('/mnt/c/Users/narut/OneDrive/Desktop/Project/techbots_Sumo_Robots/state/analysis/P2_stand_integration_raw/configured/build_metadata')
out.mkdir(exist_ok=False)
manifest = []
for profile in ('normal', 'sanitizer'):
    for rel in ('CMakeCache.txt', 'CMakeFiles/stand_integration_m0_tests.dir/flags.make', 'CMakeFiles/stand_integration_m0_tests.dir/link.txt', 'CMakeFiles/stand_integration_m1_tests.dir/flags.make', 'CMakeFiles/stand_integration_m1_tests.dir/link.txt'):
        source = work/profile/rel
        target = out/profile/rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        manifest.append({'path': str(pathlib.Path(profile)/rel), 'sha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'bytes': source.stat().st_size})
    for name in ('stand_integration_m0_tests', 'stand_integration_m1_tests'):
        source = work/profile/name
        manifest.append({'path': str(pathlib.Path(profile)/name), 'sha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'bytes': source.stat().st_size, 'binary_retained': False})
(out/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
print(json.dumps(manifest, indent=2))
