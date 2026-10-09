#!/usr/bin/env python3
"""Author-side internal consistency/tamper check. Not an independent verifier."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys


def verify_csv(path):
    with path.open() as f:
        rows=list(csv.DictReader(f))
    assert len(rows)==1500, 'expected 100*5*3 rows'
    keys=set()
    for row in rows:
        key=(row['replication'],row['scenario'],row['method'])
        assert key not in keys, 'duplicate row'
        keys.add(key)
        n=int(row['test_size']); c=int(row['covered'])
        assert n==1000 and 0<=c<=n, 'count outside range'
        assert int(row['count_x0'])+int(row['count_x1'])==n, 'group totals differ'
        assert int(row['covered_x0'])+int(row['covered_x1'])==c, 'covered total differs from group counts'
        assert abs(float(row['coverage'])-c/n)<1e-14, 'coverage differs from count'
        for g in (0,1):
            ng=int(row[f'count_x{g}']); cg=int(row[f'covered_x{g}'])
            assert 0<=cg<=ng, 'group covered outside range'
            if ng: assert abs(float(row[f'coverage_x{g}'])-cg/ng)<1e-14, 'group coverage differs'
    return len(rows)


def verify_manifest(root,path):
    files=json.loads(path.read_text())['files']
    for name, expected in files.items():
        actual=hashlib.sha256((root/name).read_bytes()).hexdigest()
        assert actual==expected, f'SHA256 mismatch: {name}'
    return len(files)


def main():
    p=argparse.ArgumentParser(); p.add_argument('--csv',type=Path); p.add_argument('--manifest',type=Path); p.add_argument('--root',type=Path,default=Path('.')); a=p.parse_args()
    if a.csv: print(f'PASS consistency: {verify_csv(a.csv)} rows')
    if a.manifest: print(f'PASS hashes: {verify_manifest(a.root,a.manifest)} files')
    return 0
if __name__=='__main__':
    try: sys.exit(main())
    except (AssertionError, ValueError, KeyError) as e: print(f'REJECTED: {e}',file=sys.stderr); sys.exit(1)
