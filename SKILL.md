---
name: agent-fact-check-verify
description: 嚴謹多來源資訊查核與可信度判定技能。用於「查證/核實/核實這個/是真的嗎/是否正確」類請求，整合政府、官方、主流媒體、事實查核站、X(Twitter)、Reddit 等來源，採用內部 100 分制規則化評分（不對使用者公開分數），對外輸出中立且整合式結論。
---

# Agent Fact Check Verify

## 核心原則
- 對外回覆不展示評分機制與分數。
- 對內可拆 claim，但對外**禁止逐條 claim 展示**。
- 對外只提供整合後結論，語氣中立，不帶立場。
- 如為錯誤資訊，直接給出正確情形。
- 如為預測資訊，不做真偽裁定，僅整理目前可查情形。
- 最後永遠附上限制聲明：
  - `⚠️ 本查核基於公開可得資訊，無法涵蓋未公開或付費牆後的內容。`

## 對外輸出格式（強制）
輸出時固定使用以下四段，順序不可更動：
1. `是否正確（簡答）`：僅可用「正確 / 錯誤 / 部分正確 / 證據不足」其一，並附一句簡答。
2. `此事的真實情形`：整合後敘述，不列逐條 claim。
3. `結論`：給出可執行的最終判斷（必要時含不確定性提醒）。
4. `相關連結（最多三個）`：最多 3 條，優先官方與高可信來源。

## 執行流程（Agent）
1. `scripts/factcheck_engine.py extract`：拆解可查證 claim。
2. 依 claim 類型分流：opinion/satire/prediction/verifiable。
3. 搜尋分三輪：官方→主流→反證（每輪最多 2 次，總 6 次）；另外可增加 X(Twitter) 多次查核（建議 3 次）作為社群佐證，且不改動官方/主流/反證三輪次數。
4. `scripts/factcheck_engine.py score`：以規則表計算內部分數。
5. `scripts/factcheck_engine.py compose`：輸出對使用者的整合回覆（不含分數）。

## 搜尋工具策略
- 預設優先使用使用者常用搜尋。
- 可選 Tavily（若環境有 `TAVILY_API_KEY`）。
- 可選 X/Reddit CLI：
  - X: `twitter-cli`（https://github.com/jackwener/twitter-cli）
  - Reddit: `rdt-cli`（https://github.com/jackwener/rdt-cli）
- CLI 未安裝時自動降級為一般網路搜尋，不中斷流程。

## 來源分級與評分
詳見：
- `references/scoring-rubric.md`
- `references/source-policy.md`

## 版本
- `1.0.4`
