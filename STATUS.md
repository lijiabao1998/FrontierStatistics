# 狀態｜2026-10-09 候選研究輪次

主線 STAT-001。問題卡10；父題保持 OPEN，未宣稱解決。

候選輪次 `20261009T102720435939Z-codex-STAT-001` 已完成低成本合成基線重現：vanilla / oracle-weighted / inverse-ratio controls，100 independent calibration replicates，5 frozen scenarios。檢索、驗收、admit、完整數值輸出、負例與獨立同樣本計算覆核見該輪 REPORT.md。

高 covariate shift 下 coverage 0.44242 → 0.90621，但 conditional-scale shift 的 weighted coverage 只有 0.63210。這是已知方法的有限合成重現，不是一般定理、可部署方案或父題完成。Draft PR 待審，不自合。
