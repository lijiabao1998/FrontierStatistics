# STAT-001: synthetic oracle-weighted conformal replication

This is a bounded reproduction of known behavior, not a new method, theorem, deployable remedy, or solution of the parent question. The parent topic card is unchanged. A separate reviewer independently replayed the frozen finite-synthetic calculations; this is not a new-data experiment or a scientific-success certificate.

## Frozen design and provenance

- Base: `3e9a457ce6a5033f405c6b98efca6c871c9eed53`.
- Governance: `9c3ae2dbaa1c814f3ef451c041dedfe3b77d926f`, protocol 2.0.0.
- Scope claim: https://github.com/lijiabao1998/FrontierStatistics/issues/3.
- Acceptance was committed locally at `dc23c40` and admitted before the first experiment. HTTPS push subsequently failed without credentials. The connector publishes equivalent trees later with different commit SHAs; external freeze publication is after computation, not prospective public preregistration. Original local commit objects are retained in `local-provenance.json`. `acceptance.json` SHA256: `3e5044ee3c360f266ae2ddaba5edf8493ae89512f8ffe371d45f2e8f060d9fa8`.
- Six fresh query strings across the four required categories, source reading extent, revisions and limitations are recorded in `round.json`. No competing research branch, round or open PR was found. Prior PRs #1 and #2 only repaired/upgraded governance and were merged.
- Purely generated synthetic data; no third-party dataset, credentials or paid service. Python 3.12.14 standard library, one CPU process, experiment wall time 4.39 seconds. 100 independent calibration replications; five fixed target settings in each, 500 calibration and 1,000 target observations per setting. No tuning, selection, repeated seeds or post-hoc threshold changes.

Source calibration has `X ~ Bernoulli(0.1)` and `Y = (1 + 3 X) epsilon`, `epsilon ~ Normal(0,1)`. The prediction center is the fixed function zero, avoiding model-fitting leakage. The target uses the frozen covariate probabilities, response locations and scale factors in `acceptance.json`. Source calibration and each scenario's target draws use separate SHA256-derived streams. Methods share each replicate's data for paired comparison.

The oracle method uses the target/source covariate ratio and includes the test point's weight as an atom at infinity. Covariate weighting assumes unchanged `Y | X`; the response-location and conditional-scale scenarios deliberately violate that condition. The inverse-ratio method is a misspecification control.

## Results

All intervals below are pointwise approximate 95% t intervals across 100 independent calibration replications, not Bernoulli intervals treating the pooled target predictions as independent. Monte Carlo standard errors and paired differences are in `summary.json`; all 1,500 raw count rows are in `replicates.csv`.

| Scenario | Vanilla coverage [95% CI] | Oracle-weighted coverage [95% CI] | Mean width: vanilla / oracle |
|---|---|---|---|
| No shift | 0.89799 [0.89465, 0.90133] | 0.89799 [0.89465, 0.90133] | 4.05 / 4.05 |
| Covariate p = 0.5 | 0.67201 [0.66765, 0.67637] | 0.90459 [0.89861, 0.91057] | 4.05 / 10.32 |
| Covariate p = 0.9 | 0.44242 [0.43751, 0.44733] | 0.90621 [0.89927, 0.91315] | 4.05 / 13.21 |
| Response location +4 | 0.04749 [0.04537, 0.04961] | 0.04749 [0.04537, 0.04961] | 4.05 / 4.05 |
| Covariate p = 0.9, conditional scale x2 | 0.24864 [0.24465, 0.25263] | 0.63210 [0.62195, 0.64225] | 4.05 / 13.21 |

At high covariate shift, the paired oracle-minus-vanilla coverage difference is 0.46379 [0.45563, 0.47195], MCSE 0.004114. Inverse-ratio weighting covers only 0.37677 [0.37268, 0.38086]. The oracle effective sample size averages 60.32 of 500, and its wider intervals matter when interpreting the coverage improvement.

Marginal success hides subgroup failure: even without shift, vanilla group `X=1` coverage is 0.38852 [0.37752, 0.39952], whereas group `X=0` coverage is 0.95525. No conditional/subgroup-validity claim is made.

All nine frozen statistical criteria passed on the first and only stochastic execution. Nine deterministic tests passed, including a high-test-weight infinity boundary, equal-weight agreement, weight association, ties, invalid inputs, ratio normalization and stream separation. The deliberate quantile mutant and corrupted count file both exited 1 as intended; their complete failure logs are retained. Governance's 168 tests passed. These checks verify limited behavior and record consistency, not scientific truth.

## Interpretation limits

- Known density ratios and a tiny fully specified DGP are an oracle benchmark. Estimated ratios, poor overlap, arbitrary conditional shift and real data remain untested.
- These are approximate Monte Carlo uncertainty intervals, not formal finite-sample certificates. They are pointwise; no simultaneous or multiple-testing claim is made. The subgroup estimates average each replication's subgroup coverage rather than pooling counts.
- Boundary t intervals such as `[0,0]` for no observed infinite intervals or `[1,1]` for all-covered subgroups indicate zero observed replicate variance. They do not certify population probabilities of zero or one.
- `width_mean` is the mean finite interval width and is interpreted alongside `infinite_rate`. Every interval in this particular run was finite; this need not hold in other settings.
- Bias, variance and RMSE fields describe errors of the fixed-zero point predictor. Power, FDR and causal identification are not estimands of this experiment.
- There was no fitted/tuned candidate and no use of these test outcomes to choose acceptance. Independent review uses archived draws and a separately written calculation; rerunning the author's script alone is not independent validation.

## Literature boundary

[Tibshirani, Barber, Candes and Ramdas (2019)](https://papers.neurips.cc/paper_files/paper/2019/file/8fb21ee7a2207526da55a679f0332de2-Paper.pdf), relevant full-text sections 1–2 and Corollary 1, establish the oracle covariate-shift construction being reproduced. [Pournaderi and Xiang, v3 (2025)](https://arxiv.org/html/2405.16594v3), relevant full-text sections 2.3–3.1, distinguish marginal from calibration-conditional coverage and state assumptions for stronger bounds. The [September 2026 preprint](https://arxiv.org/abs/2609.33456) was read at abstract/submission-history level only and is an explicit novelty warning. No proof in these papers was independently certified in this round; no full paper text or external dataset is redistributed.

## Failures and work not done

- Initial official GitHub clone was interrupted during tool polling by `automatic approval review was cancelled`; a later read-only fetch completed the checkout. This was setup failure, not a failed statistical run.
- Expected negative-control logs: `tamper-negative.log` and `quantile-mutant-negative.log`.
- NOT_RUN: learned-density ratios, real-world data, formal proof, deployment, parent-problem completion, merge.
- Independent review received the frozen spec before experiments. Its `independent-review.json` reports exact agreement for all 1,500 rows, 16,500 archived float-hex input pairs, every weighted quantile and all 15 coverage intervals; the largest width discrepancy is 3.55e-15. It used a separate exact-integer weighting implementation with no author imports. This is same-sample independent computational replay, not independent data. The author invalid-input and tamper harness was not independently rerun. The verifier implementation is reserved for a separate review PR. Report SHA256: `a0686ad787b53c33bf989154cd905fc5c44cecd1731869dc9fbbfe0ab570430b`; verifier code SHA256: `3e708cc9580c6d27cc6ece13a87e1a80f4fc7be32fc112d0cbc07a315a6ed088`.
