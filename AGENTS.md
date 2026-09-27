# FrontierStatistics agent 入口

先讀 README、STATUS、VALIDATION 與固定治理 https://github.com/lijiabao1998/FrontierLab-Governance/tree/091d6a26a4af8522683711483f2b97afd90efa7f 。
所有 agent 用 <agent>/STAT-xxx-<topic> 分支；不直接 main、不自合。每輪 start → fresh literature search → 凍結 estimand/assumptions/acceptance → admit → baseline → exploration → independent verifier/skeptic → PR。

統計特別規則：識別條件、估計器、finite-sample/asymptotic statement、資料生成機制分開；coverage/FDR/type-I/power 都報區間與 Monte Carlo error。不得用同一 simulation 設定調參又當獨立驗證。
