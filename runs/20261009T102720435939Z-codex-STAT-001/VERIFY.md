# Reproduction and independent verification

Use a clean checkout of this candidate branch and CPython 3.12.14 for byte-identical synthetic streams. No packages, secrets, accounts or paid resources are needed. Keep reproduction output in a temporary directory so archived results are not overwritten.

```sh
python3 -m unittest discover -s problems/STAT-001/experiments -p 'test_*.py' -v
python3 problems/STAT-001/experiments/verify_artifacts.py --csv problems/STAT-001/results/20261009T102720435939Z-codex-STAT-001/replicates.csv
python3 problems/STAT-001/experiments/synthetic_shift.py \
  --spec runs/20261009T102720435939Z-codex-STAT-001/acceptance.json \
  --out /tmp/stat001-reproduction
cmp /tmp/stat001-reproduction/replicates.csv problems/STAT-001/results/20261009T102720435939Z-codex-STAT-001/replicates.csv
cmp /tmp/stat001-reproduction/input_hashes.json problems/STAT-001/results/20261009T102720435939Z-codex-STAT-001/input_hashes.json
cmp /tmp/stat001-reproduction/summary.json problems/STAT-001/results/20261009T102720435939Z-codex-STAT-001/summary.json
```

The same frozen seeds reproduce the existing 100 unique calibration replications; this is not an independent experiment. Runtime/environment metadata naturally differ. The synthetic generator plus exact seed/hash table specifies all inputs. For independent checks, `raw_selected.json` archives every calibration/test `(x,y,y.hex())` in replications 0, 1 and 99, with exact IEEE-754 values available through `float.fromhex`.

A verifier must not import the author's experiment or summarizer:

1. Read `acceptance.json` from the original local pre-experiment commit or the connector-published freeze snapshot and check its hash. Audit original local objects in `local-provenance.json` and admission ordering. Connector publication occurred after computation, so do not call it prospective public preregistration.
2. Independently implement sorting/cumulative weights with the test-point infinity atom; recover both group thresholds from the archived calibration data.
3. Independently count coverage on each archived target sample for every method/scenario and compare all selected CSV rows. Confirm the inverse-ratio negative control uses source/target rather than target/source weighting.
4. Use the standard normal CDF to compute exact conditional-on-calibration target coverage for a given pair of thresholds: sum the two group probabilities times `Phi((q_g - location)/sigma_g) - Phi((-q_g - location)/sigma_g)`, with `sigma_g = scale*(1+3*g)`. This validates distribution semantics without another stochastic run.
5. Recompute replicate-level sample variance, MCSE and t99 intervals and paired method differences from all raw rows. Check subgroup totals, no-shift equality, width and infinity-rate reporting. Try omitting the infinity atom and altering a raw count; fixed controls must reject both.
6. Audit claims against read sources. Do not treat author-side consistency, governance pass, identical rerun, or reviewer agreement as a universal coverage proof.

Governance is a separate pinned checkout:

```sh
git clone https://github.com/lijiabao1998/FrontierLab-Governance.git /tmp/stat001-governance
git -C /tmp/stat001-governance checkout --detach 9c3ae2dbaa1c814f3ef451c041dedfe3b77d926f
(cd /tmp/stat001-governance && python3 -m unittest discover -s tests -v)
python3 /tmp/stat001-governance/tools/frontier.py validate .
python3 /tmp/stat001-governance/tools/frontier.py check-pins .
python3 /tmp/stat001-governance/tools/frontier.py check-diff . 3e9a457ce6a5033f405c6b98efca6c871c9eed53 HEAD
```

Stop on any inconsistency; retain logs and do not alter acceptance to make the result pass. No merge or publication of a scientific-success claim is authorized by these checks.
