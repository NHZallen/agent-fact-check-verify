---
name: agent-fact-check-verify
description: 嚴謹多來源資訊查核與可信度判定技能。用於「查證/核實/核實這個/是真的嗎/是否正確」類請求，整合政府、官方、主流媒體、事實查核站、X(Twitter)、Reddit 等來源，採用內部 100 分制規則化評分（不對使用者公開分數），並強制 Tavily 優先與明確 fallback 規則。
---

# Agent Fact Check Verify

## 核心原則
- 對外回覆不展示評分機制與分數。
- 對內可拆 claim，但對外**禁止逐條 claim 展示**。
- 對外只提供整合後結論，語氣中立，不帶立場。
- 如為錯誤資訊，直接給出正確情形。
- 如為預測資訊，不做真偽裁定，僅整理目前可查情形。
- 採用「**Claim Core First**」：先判斷核心主張，再看細節；非關鍵細節不得翻盤。
- 最後永遠附上限制聲明：
  - `⚠️ 本查核基於公開可得資訊，無法涵蓋未公開或付費牆後的內容。`

## 對外輸出格式（強制）
輸出時固定使用以下四段，順序不可更動：
1. `是否正確（簡答）`：僅可用「正確 / 錯誤 / 部分正確 / 證據不足」其一，並附一句簡答。
2. `此事的真實情形`：整合後敘述，不列逐條 claim。
3. `結論`：給出可執行的最終判斷（必要時含不確定性提醒）。
4. `相關連結（最多三個）`：最多 3 條，優先官方與高可信來源。

## 判定層級（避免重點誤判）
1. **核心事實層（最高權重）**：事件是否發生、主體是否正確、方向是否正確。
2. **關鍵條件層（中權重）**：時間/地點/對象等僅在會改變真假時加權。
3. **表述細節層（低權重）**：快訊語氣、措辭、非關鍵描述，原則不得單獨導致「錯誤」。

> 例：貼文稱「快訊」，但內容本體為真僅時間非即時，優先判「部分正確」或「脈絡不足」，除非其核心主張就是「此刻剛發生」。

## 搜尋工具策略（強制 Tavily + Fallback）
- **強制 Tavily 優先**：只要有 `TAVILY_API_KEY` 且 Tavily 可用，所有一般搜尋先走 Tavily。
- 僅在以下情況可 fallback 到預設搜尋：
  - `TAVILY_API_KEY` 缺失
  - `401/403` 認證失敗
  - `429` 或 quota exhausted
  - 連續 timeout / service unavailable
- fallback 不得中斷流程，需標記該輪為 fallback。

## 來源配比與查詢預算
- 預設來源配比：
  - **Tavily（或 fallback 搜尋）50%**
  - **Reddit CLI 10%**
  - **Twitter CLI 40%**
- 預設總查詢上限：**每主題 10 次**。
- 強制最低查詢次數（避免象徵性呼叫）：
  - **Tavily 至少 5 次**
  - **Twitter CLI 至少 4 次**
  - **Reddit CLI 至少 1 次**

### CLI 缺失時重分配（強制）
- Reddit 不可用（缺 10%）：重分配為 **Tavily +7%**、**可信度交叉驗證 +3%**。
- Twitter 不可用（缺 40%）：重分配為 **Tavily +28%**、**可信度交叉驗證 +12%**。
- Reddit+Twitter 皆不可用：等效 **Tavily 85% + 可信度交叉驗證 15%**。
- 缺失工具的最低次數，全部轉為 Tavily 與可信度交叉驗證的追加查詢，不得省略總量。

### 查詢次數提升（強制）
- CLI 都可用：上限 **10 次**。
- 缺 1 個 CLI：上限 **12 次**。
- 缺 2 個 CLI：上限 **14 次**。

## 執行流程（Agent）
1. `scripts/factcheck_engine.py extract`：拆解可查證 claim。
2. 依 claim 類型分流：opinion/satire/prediction/verifiable。
3. 套用「Claim Core First」標註核心與次要條件，避免細節誤判。
4. 依來源配比分配查詢，先走 Tavily，必要時 fallback。
5. `scripts/factcheck_engine.py score`：以規則表計算內部分數。
6. `scripts/factcheck_engine.py compose`：輸出對使用者的整合回覆（不含分數）。

## 來源分級與評分
詳見：
- `references/scoring-rubric.md`
- `references/source-policy.md`

## 版本
- `1.0.5`
