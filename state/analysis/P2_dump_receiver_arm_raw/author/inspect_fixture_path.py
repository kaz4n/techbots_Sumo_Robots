"""Read-only inventory of the exact synthetic ticket path from first fixture run."""
import json
import os
from pathlib import Path
import stat

raw = Path(__file__).resolve().parent
path = Path('/tmp/sumox26-dump-connection-0123456789abcdef0123456789abcdef')
report = {'path':str(path),'exists':path.exists(),'symlink':path.is_symlink(),'entries':[],'cleanup_performed':False}
if path.exists() and not path.is_symlink():
    for child in path.iterdir():
        info = child.lstat()
        item = {'name':child.name,'mode':oct(stat.S_IMODE(info.st_mode)),'uid':info.st_uid,
                'size':info.st_size,'inode':info.st_ino,'device':info.st_dev}
        if stat.S_ISREG(info.st_mode) and info.st_size <= 4096:
            item['text'] = child.read_text(errors='replace')
        report['entries'].append(item)
(raw/'first_fixture_real_tmp_inventory.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
