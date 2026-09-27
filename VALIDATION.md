# 統計驗證契約

每個子任務先寫 estimand、data-generating process、identification assumptions、sampling scheme、missingness/interference/shift mechanism、primary error criterion 與 Monte Carlo budget。

- finite-sample guarantee 與 asymptotic guarantee 不混用。
- coverage、FDR、type-I error 先用已知真值合成資料校準，再碰真實資料。
- 估計 bias、variance、RMSE、interval width、power 同時看，不只挑單一指標。
- 需要 nuisance ML 時做 cross-fitting / sample splitting；資料洩漏和 tuning leakage 單獨檢查。
- causal claim 必須明列 exchangeability / positivity / consistency / interference assumptions。
- sensitivity analysis 不能被描述成 point identification。
