"""Run portable reviewer on corrupted temporary copies; never edit archive."""
import csv,json,pathlib,shutil,subprocess,sys,tempfile
repo=pathlib.Path(sys.argv[1]).resolve();script=pathlib.Path(__file__).with_name('verify_statistics.py');outputs=[]
for case in ['covered_count','frozen_spec']:
 with tempfile.TemporaryDirectory() as temp:
  root=pathlib.Path(temp)/'copy';root.mkdir()
  for part in ['problems/STAT-001/results/20261009T102720435939Z-codex-STAT-001','runs/20261009T102720435939Z-codex-STAT-001']:
   shutil.copytree(repo/part,root/part)
  if case=='covered_count':
   p=root/'problems/STAT-001/results/20261009T102720435939Z-codex-STAT-001/replicates.csv';rows=list(csv.DictReader(p.open()));keys=list(rows[0]);rows[0]['covered']=str(int(rows[0]['covered'])+1)
   with p.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)
  else:
   p=root/'runs/20261009T102720435939Z-codex-STAT-001/acceptance.json';p.write_text(p.read_text()+' ')
  r=subprocess.run([sys.executable,str(script),str(root),str(pathlib.Path(temp)/'out')],capture_output=True,text=True,timeout=30)
  assert r.returncode!=0,case
  outputs.append({'case':case,'rejected':True,'exit_code':r.returncode,'reason':r.stderr.splitlines()[-1]})
print(json.dumps(outputs,indent=2))
