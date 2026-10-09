"""Independent integer-mass conformal evaluator and summary checker.

Does not import or execute author code. Replays exactly the frozen inputs.
"""
import csv,hashlib,json,math,random,statistics
from fractions import Fraction
from pathlib import Path
import sys
REPO=Path(sys.argv[1]).resolve()
ROOT=Path(sys.argv[2]).resolve()
ROOT.mkdir(parents=True,exist_ok=True)
STAT=REPO/"runs/20261009T102720435939Z-codex-STAT-001/acceptance.json"

R=REPO/"problems/STAT-001/results/20261009T102720435939Z-codex-STAT-001"
def sample(rep,stream,n,p,loc=0,scale=1):
    seed=int.from_bytes(hashlib.sha256(f'202610091:{rep}:{stream}'.encode()).digest(),'big')
    rng=random.Random(seed);out=[]
    for _ in range(n):
        x=int(rng.random()<p);y=loc+scale*(1+3*x)*rng.gauss(0,1);out.append((x,y))
    return out
def qs(cal,p,method):
    if method=='vanilla':return [sorted(abs(y) for _,y in cal)[450]]*2
    ratios=[(1-Fraction(str(p)))/Fraction('0.9'),Fraction(str(p))/Fraction('0.1')]
    if method=='wrong_ratio':ratios=[1/r for r in ratios]
    denom=math.lcm(*(r.denominator for r in ratios)); w=[int(r*denom) for r in ratios]
    mass=sum(w[x] for x,_ in cal);ordered=sorted((abs(y),w[x]) for x,y in cal);out=[]
    for testx in (0,1):
        target=9*(mass+w[testx]);cum=0;q=math.inf
        for score,weight in ordered:
            cum+=weight
            if 10*cum>=target:q=score;break
        out.append(q)
    return out
def main():
    assert hashlib.sha256(STAT.read_bytes()).hexdigest()=='3e5044ee3c360f266ae2ddaba5edf8493ae89512f8ffe371d45f2e8f060d9fa8'
    spec=json.loads(STAT.read_text()); scenarios=spec['scenarios']; summary=json.loads((R/'summary.json').read_text())
    rows=list(csv.DictReader((R/'replicates.csv').open()));assert len(rows)==1500
    idx={(int(r['replication']),r['scenario'],r['method']):r for r in rows}; assert len(idx)==1500
    archived={(r['replication'],r['stream']):r['points'] for r in json.loads((R/'raw_selected.json').read_text())}
    verified_points=0;max_q_gap=0;max_width_gap=0;checks=0
    for rep in range(100):
        cal=sample(rep,'calibration',500,.1)
        if (rep,'calibration') in archived:
            assert all(x==a[0] and y==float.fromhex(a[2]) and y==a[1] for (x,y),a in zip(cal,archived[(rep,'calibration')]))
            verified_points+=len(cal)
        for s in scenarios:
            name=s['name'];test=sample(rep,name,1000,s['target_p'],s['location'],s['scale'])
            if (rep,name) in archived:
                assert all(x==a[0] and y==float.fromhex(a[2]) and y==a[1] for (x,y),a in zip(test,archived[(rep,name)]))
                verified_points+=len(test)
            for method in ('vanilla','oracle_weighted','wrong_ratio'):
                r=idx[rep,name,method];q=qs(cal,s['target_p'],method)
                counts=[sum(x==g for x,y in test) for g in (0,1)]
                covered=[sum(x==g and abs(y)<=q[g] for x,y in test) for g in (0,1)]
                assert counts==[int(r['count_x0']),int(r['count_x1'])]
                assert covered==[int(r['covered_x0']),int(r['covered_x1'])]
                assert sum(covered)==int(r['covered']) and float(r['coverage'])==sum(covered)/1000
                qgap=max(abs(q[g]-float(r[f'q{g}'])) for g in (0,1));max_q_gap=max(max_q_gap,qgap);assert qgap==0
                width=math.fsum(2*q[x] for x,y in test)/1000;wgap=abs(width-float(r['width_mean']));max_width_gap=max(max_width_gap,wgap);assert wgap<1e-12
                checks+=1
    max_summary_gap=0;out_cells={}
    for key,cell in summary['cells'].items():
        scenario,method=key.split('/');vals=[float(idx[rep,scenario,method]['coverage']) for rep in range(100)]
        mean=statistics.mean(vals);se=statistics.stdev(vals)/10;ci=[mean-1.9842169515086827*se,mean+1.9842169515086827*se]
        max_summary_gap=max(max_summary_gap,abs(mean-cell['coverage']['mean']),abs(se-cell['coverage']['mcse']),*(abs(a-b) for a,b in zip(ci,cell['coverage']['ci95'])))
        assert max_summary_gap<1e-14
        out_cells[key]={'mean':mean,'mcse':se,'ci95':ci}
    def cc(k):return out_cells[k]
    acceptance={
        'no_shift_mean':.87<=cc('no_shift/vanilla')['mean']<=.93,
        'no_shift_exact_equal':all(idx[rep,'no_shift','vanilla']['covered']==idx[rep,'no_shift','oracle_weighted']['covered'] and idx[rep,'no_shift','vanilla']['q0']==idx[rep,'no_shift','oracle_weighted']['q0'] and idx[rep,'no_shift','vanilla']['q1']==idx[rep,'no_shift','oracle_weighted']['q1'] for rep in range(100)),
        'covariate_high_failure':cc('covariate_high/vanilla')['ci95'][1]<.85,
        'covariate_high_repair':cc('covariate_high/oracle_weighted')['ci95'][0]>.87 and cc('covariate_high/oracle_weighted')['ci95'][1]<.95,
        'width':statistics.mean(float(idx[rep,'covariate_high','oracle_weighted']['width_mean']) for rep in range(100))<16,
        'no_infinities':all(float(idx[rep,'covariate_high','oracle_weighted']['infinite_rate'])==0 for rep in range(100)),
        'conditional_scale_limit':cc('conditional_scale/oracle_weighted')['ci95'][1]<.80,
        'location_limit':cc('location_shift/oracle_weighted')['ci95'][1]<.50,
        'wrong_ratio':cc('covariate_high/wrong_ratio')['ci95'][1]<.85}
    assert all(acceptance.values())
    out={'verdict':'INDEPENDENT_FINITE_SYNTHETIC_CHECK_PASS','scope':'Independent exact-integer weighted-mass quantiles, deterministic replay of same frozen samples, counts and replicate-level coverage CIs. Not independent new data, a new method, a theorem, conditional coverage or practical estimated-ratio guarantee. Author invalid-input test suite not independently rerun here.','rows_verified':checks,'archived_points_hex_verified':verified_points,'max_quantile_gap':max_q_gap,'max_width_gap':max_width_gap,'max_summary_gap':max_summary_gap,'acceptance':acceptance,'cells':out_cells,'spec_sha256':hashlib.sha256(STAT.read_bytes()).hexdigest()}
    (ROOT/'statistics-independent-review.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='cells'},indent=2))
if __name__=='__main__':main()
