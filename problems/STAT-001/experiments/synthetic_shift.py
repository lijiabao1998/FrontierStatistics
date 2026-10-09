#!/usr/bin/env python3
"""Bounded synthetic REPLICATION. Python stdlib only; no universal-coverage claim."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import platform
import random
import statistics
import sys
import time

T99 = 1.9842169515086827
METHODS = ('vanilla', 'oracle_weighted', 'wrong_ratio')


def weighted_quantile(scores, weights, test_weight, alpha):
    """Quantile of sum(w_i delta_score_i)+w_test delta_inf, normalized jointly."""
    if len(scores) != len(weights) or not scores:
        raise ValueError('scores and weights must have equal nonzero length')
    if not 0 < alpha < 1 or not math.isfinite(test_weight) or test_weight <= 0:
        raise ValueError('alpha/test weight outside admissible range')
    if any(not math.isfinite(v) or v < 0 for v in scores):
        raise ValueError('absolute residual scores must be finite and nonnegative')
    if any(not math.isfinite(w) or w <= 0 for w in weights):
        raise ValueError('weights must be finite and strictly positive')
    threshold = (1-alpha) * (math.fsum(weights) + test_weight)
    cumulative = 0.0
    # Sorting the paired samples keeps their associated importance weights.
    for score, weight in sorted(zip(scores, weights)):
        cumulative += weight
        if cumulative >= threshold:
            return score
    return math.inf


def vanilla_quantile(scores, alpha):
    if not scores or not 0 < alpha < 1:
        raise ValueError('invalid calibration size or alpha')
    rank = math.ceil((len(scores) + 1) * (1-alpha))
    return sorted(scores)[rank-1] if rank <= len(scores) else math.inf


def seed(master, replication, stream):
    return int.from_bytes(hashlib.sha256(f'{master}:{replication}:{stream}'.encode()).digest(), 'big')


def draw(n, p, location, scale, rng):
    result = []
    for _ in range(n):
        x = int(rng.random() < p)
        result.append((x, location + scale * (1 + 3*x) * rng.gauss(0, 1)))
    return result


def digest_data(data):
    # Hex float records are a lossless platform-readable representation.
    payload = ''.join(f'{x},{y.hex()}\n' for x, y in data).encode()
    return hashlib.sha256(payload).hexdigest()


def ratio(x, target_p, source_p):
    return target_p/source_p if x else (1-target_p)/(1-source_p)


def interval(values, bounded=False):
    mean = statistics.mean(values)
    se = statistics.stdev(values) / math.sqrt(len(values))
    lo, hi = mean-T99*se, mean+T99*se
    return {'mean':mean, 'mcse':se, 'ci95':[max(0.,lo),min(1.,hi)] if bounded else [lo,hi], 'replications':len(values)}


def summarize(rows):
    cells = {}
    for scenario in sorted({row['scenario'] for row in rows}):
        for method in METHODS:
            rr = [row for row in rows if row['scenario']==scenario and row['method']==method]
            metrics = {}
            for field in ('coverage','coverage_x0','coverage_x1','width_mean','infinite_rate','ess','mean_error','error_variance','rmse'):
                values = [row[field] for row in rr if row[field] is not None]
                metrics[field] = interval(values, field.startswith('coverage') or field=='infinite_rate') if len(values)>1 else None
            metrics['covered_total'] = sum(r['covered'] for r in rr)
            metrics['test_total'] = sum(r['test_size'] for r in rr)
            cells[f'{scenario}/{method}'] = metrics
    gaps={}
    for scenario in sorted({row['scenario'] for row in rows}):
        by_rep={}
        for row in rows:
            if row['scenario']==scenario:
                by_rep.setdefault(row['replication'],{})[row['method']]=row['coverage']
        gaps[scenario]=interval([d['oracle_weighted']-d['vanilla'] for d in by_rep.values()])
    c=lambda s,m:cells[f'{s}/{m}']['coverage']
    identical=all(row['q0']==other['q0'] and row['q1']==other['q1'] and row['covered']==other['covered'] for row,other in zip(
        [r for r in rows if r['scenario']=='no_shift' and r['method']=='vanilla'],
        [r for r in rows if r['scenario']=='no_shift' and r['method']=='oracle_weighted']))
    checks={
        'no_shift_mean':0.87 <= c('no_shift','vanilla')['mean'] <= 0.93,
        'no_shift_identical':identical,
        'high_covariate_vanilla_failure':c('covariate_high','vanilla')['ci95'][1] < 0.85,
        'high_covariate_oracle_repair':c('covariate_high','oracle_weighted')['ci95'][0] > 0.87 and c('covariate_high','oracle_weighted')['ci95'][1] < 0.95,
        'high_covariate_width':cells['covariate_high/oracle_weighted']['width_mean']['mean'] < 16,
        'high_covariate_no_infinite':cells['covariate_high/oracle_weighted']['infinite_rate']['mean'] == 0,
        'conditional_scale_limit':c('conditional_scale','oracle_weighted')['ci95'][1] < 0.80,
        'location_limit':c('location_shift','oracle_weighted')['ci95'][1] < 0.50,
        'wrong_ratio_failure':c('covariate_high','wrong_ratio')['ci95'][1] < 0.85,
    }
    return {'evidence':'synthetic simulation only; author checks, not independent certification', 'interval_method':'pointwise approximate t99 across 100 independent calibration replicates; subgroup means are unweighted across replicates', 'cells':cells,'paired_coverage_gaps':gaps,'frozen_statistical_checks':checks,'all_statistical_checks_pass':all(checks.values())}


def execute(spec, out):
    out.mkdir(parents=True, exist_ok=True)
    rows=[]; input_hashes=[]; raw_selected=[]; alpha=spec['alpha']; source_p=spec['source_dgp']['p']
    for rep in range(spec['replications']):
        cs=seed(spec['master_seed'],rep,'calibration')
        cal=draw(spec['calibration_size'],source_p,0.,1.,random.Random(cs))
        input_hashes.append({'replication':rep,'stream':'calibration','seed':str(cs),'n':len(cal),'sha256_hex_records':digest_data(cal)})
        if rep in (0,1,99):
            raw_selected.append({'replication':rep,'stream':'calibration','points':[[x,y,y.hex()] for x,y in cal]})
        scores=[abs(y) for _,y in cal]
        vanilla=vanilla_quantile(scores,alpha)
        for setting in spec['scenarios']:
            name=setting['name']; ts=seed(spec['master_seed'],rep,name)
            target=draw(spec['test_size_per_scenario'],setting['target_p'],setting['location'],setting['scale'],random.Random(ts))
            input_hashes.append({'replication':rep,'stream':name,'seed':str(ts),'n':len(target),'sha256_hex_records':digest_data(target)})
            if rep in (0,1,99):
                raw_selected.append({'replication':rep,'stream':name,'points':[[x,y,y.hex()] for x,y in target]})
            oracle=[ratio(x,setting['target_p'],source_p) for x,_ in cal]
            for method in METHODS:
                weights=[1.]*len(cal) if method=='vanilla' else oracle if method=='oracle_weighted' else [1/w for w in oracle]
                q=[]
                for group in (0,1):
                    tw=ratio(group,setting['target_p'],source_p)
                    if method=='wrong_ratio': tw=1/tw
                    q.append(vanilla if method=='vanilla' else weighted_quantile(scores,weights,tw,alpha))
                counts=[sum(x==g for x,_ in target) for g in (0,1)]
                covers=[sum(x==g and abs(y)<=q[g] for x,y in target) for g in (0,1)]
                inf=sum(math.isinf(q[x]) for x,_ in target)
                finite_widths=[2*q[x] for x,_ in target if math.isfinite(q[x])]
                ys=[y for _,y in target]
                row={'replication':rep,'scenario':name,'method':method,'test_size':len(target), 'covered':sum(covers),'count_x0':counts[0],'count_x1':counts[1],'covered_x0':covers[0],'covered_x1':covers[1], 'coverage':sum(covers)/len(target),'coverage_x0':covers[0]/counts[0] if counts[0] else None,'coverage_x1':covers[1]/counts[1] if counts[1] else None,'q0':q[0],'q1':q[1],'width_mean':statistics.mean(finite_widths) if finite_widths else None,'infinite_rate':inf/len(target),'ess':sum(weights)**2/sum(w*w for w in weights),'mean_error':-statistics.mean(ys),'error_variance':statistics.variance(ys),'rmse':math.sqrt(statistics.mean(y*y for y in ys))}
                # Finite width is explicitly separate from infinite intervals; planned case has none.
                rows.append(row)
    with (out/'replicates.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    (out/'input_hashes.json').write_text(json.dumps(input_hashes,indent=2)+'\n')
    (out/'raw_selected.json').write_text(json.dumps(raw_selected,separators=(',',':'))+'\n')
    summary=summarize(rows)
    (out/'summary.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    return summary


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--spec',type=Path,required=True); parser.add_argument('--out',type=Path,required=True); a=parser.parse_args()
    spec=json.loads(a.spec.read_text()); started=time.perf_counter()
    summary=execute(spec,a.out)
    (a.out/'environment.json').write_text(json.dumps({'python':sys.version,'platform':platform.platform(),'implementation':platform.python_implementation(),'dependencies':'stdlib only','elapsed_seconds':time.perf_counter()-started,'spec_sha256':hashlib.sha256(a.spec.read_bytes()).hexdigest()},indent=2)+'\n')
    for key,val in summary['cells'].items():
        c=val['coverage']; print(f"{key}: coverage={c['mean']:.6f} CI95={c['ci95']} MCSE={c['mcse']:.6f} width={val['width_mean']['mean']:.6f}")
    print(json.dumps(summary['frozen_statistical_checks'],indent=2))
    return 0 if summary['all_statistical_checks_pass'] else 1

if __name__=='__main__': sys.exit(main())
