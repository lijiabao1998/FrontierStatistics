# FrontierStatistics
前沿統計學

## 主線：識別條件 → finite-sample / asymptotic 保證 → 壓力測試 → 外部泛化
第一輪 **STAT-001：distribution shift 下的 conformal coverage**，先以合成分布重現 coverage failure 與修正，不直接上大模型。

| ID | 問題 | 優先 |
|---|---|---|
| STAT-001 | Distribution shift 下的 conformal coverage | A |
| STAT-002 | Selective inference 與 FCR/FDR control | A |
| STAT-003 | Network interference 下的因果識別 | B |
| STAT-004 | Multi-source / target transportability | B |
| STAT-005 | MNAR missingness 的可識別性與敏感性 | B |
| STAT-006 | 高維 nuisance + ML 的有效推論 | A |
| STAT-007 | 強依賴多重檢定的 FDR control | B |
| STAT-008 | Distribution shift 下 calibration | A |
| STAT-009 | Nonstationary time-series forecast uncertainty | B |
| STAT-010 | Benchmark/model selection 後推論有效性 | B |

每輪依治理 9c3ae2dbaa1c814f3ef451c041dedfe3b77d926f 做 fresh search、凍結 estimand/assumptions/evaluator，再進實驗。OPEN 只是初始篩查狀態。
