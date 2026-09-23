"""Runs reviewer-only cases and retains exact drafts and subprocess evidence."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import time

ROOT=Path(__file__).resolve().parents[3]
folder=Path(__file__).resolve().parent/('boundary_'+str(time.time_ns()))
folder.mkdir()
os.environ['SUMO_NATIVE_RECEIPT_DIR']=str(folder)
for name in ('imu_bus_unoq.cpp','imu_bus_unoq.h'):
    shutil.copyfile(ROOT/'src/hal'/name,folder/name)
shutil.copyfile(Path(__file__).with_name('final_boundary_review.cc'),folder/'final_boundary_review.cc')
shutil.copyfile(ROOT/'src/config.h',folder/'config.h')
spec=importlib.util.spec_from_file_location('author_runner',ROOT/'tests/tooling/test_imu_bus_unoq.py')
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
tests=module.NativeImuBusTests
tests.setUpClass()
try:
    binary=tests.variant(str(Path(__file__).with_name('final_boundary_review.cc')))
    result=tests.command([str(binary),'--no-colors'],expected=int(os.environ.get('EXPECTED_REVIEW_STATUS','1')))
    print(result.stdout)
finally:
    tests.doClassCleanups()
print(folder)
