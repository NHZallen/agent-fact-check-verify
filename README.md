# Agent Fact Check Verify

版本：**1.0.0**  
作者：**Allen Niu**  
授權：**MIT**

這是一個給 AI Agent 使用的嚴謹查核技能。它會把輸入文字拆成可驗證 claim，整合官方來源、主流媒體、事實查核站與社群訊號（X/Reddit），在內部用規則化 100 分制做判定，最後回覆使用者時只輸出中立、整合式結論，不顯示評分細節。

## 目錄

- [1. 目標與設計原則](#1-目標與設計原則)
- [2. 功能範圍](#2-功能範圍)
- [3. 非功能需求](#3-非功能需求)
- [4. 專案結構](#4-專案結構)
- [5. 安裝](#5-安裝)
- [6. CLI 工具（可選）與 Cookie 類別](#6-cli-工具可選與-cookie-類別)
- [7. 使用流程](#7-使用流程)
- [8. 輸入與輸出資料格式](#8-輸入與輸出資料格式)
- [9. 判定策略（對外不顯示分數）](#9-判定策略對外不顯示分數)
- [10. 回覆風格規範](#10-回覆風格規範)
- [11. 限制與風險](#11-限制與風險)
- [12. 多語文件](#12-多語文件)

## 1. 目標與設計原則

本技能解決的是「資訊真偽查核」與「可追溯證據整合」問題，不做情緒煽動，不做立場宣傳。

設計原則：

1. **可重現**：同一份 evidence 輸入，得到同一判定。
2. **可追溯**：每個結論都可回溯到來源連結。
3. **中立表達**：輸出敘述不帶主觀立場。
4. **對外簡潔**：不向使用者暴露內部分數機制。
5. **效率可控**：每個 claim 有固定搜索預算（建議上限 6 次）。

## 2. 功能範圍

- Claim 拆解：把長句拆成可查證單元。
- Claim 分類：statistical / causal / attribution / event / prediction / opinion / satire。
- 多來源查核：官方、主流、反證、社群訊號。
- 內部評分：規則化 100 分制（internal only）。
- 對外回覆：只輸出結論與整合敘述，不顯示內部分數。

## 3. 非功能需求

- 對外輸出預設中文。
- 錯誤訊息優先回覆，其次存疑，最後正確。
- 非必要不使用條列。
- 永遠附上限制聲明：

`⚠️ 本查核基於公開可得資訊，無法涵蓋未公開或付費牆後的內容。`

## 4. 專案結構

```text
agent-fact-check-verify/
├── SKILL.md
├── LICENSE
├── README.md
├── scripts/
│   └── factcheck_engine.py
├── references/
│   ├── scoring-rubric.md
│   └── source-policy.md
└── docs/
    ├── README.en.md
    ├── README.es.md
    └── README.ar.md
```

## 5. 安裝

### 5.1 系統需求

- Python 3.10+
- 可用於搜尋的 Agent 工具鏈（如 Brave / Tavily / Browser）

### 5.2 權限需求

- 能讀寫工作目錄
- 能呼叫搜尋工具

### 5.3 基本驗證

```bash
python3 scripts/factcheck_engine.py --help
```

## 6. CLI 工具（可選）與 Cookie 類別

以下兩個 CLI **是可選項**，不是強制。未安裝時可退回一般網頁搜尋。

- X 搜索：<https://github.com/jackwener/twitter-cli>
- Reddit 搜索：<https://github.com/jackwener/rdt-cli>

### 6.1 twitter-cli 常見 Cookie 類別

實際欄位以你安裝版本文件為準，常見分類如下：

- 必要：`auth_token`, `ct0`
- 常見輔助：`guest_id`, `kdt`
- 可能出現：`twid`, `lang`

建議：

- 只在本機安全環境保存 cookie。
- 避免把 cookie 寫入版本庫。

### 6.2 rdt-cli 常見 Cookie/Session 類別

實際欄位以你安裝版本文件為準，常見分類如下：

- Session 類：`reddit_session`
- 裝置/追蹤類：`loid`, `session_tracker`
- 其他可能欄位：`token_v2` 或同類授權 cookie

建議：

- 優先使用官方 OAuth 流程（若 CLI 支援）。
- 若必須 cookie 登入，請使用最小權限帳號並定期更換。

## 7. 使用流程

### 7.1 抽取 claim

```bash
python3 scripts/factcheck_engine.py extract \
  --text "輸入待查文字" \
  --output claims.json
```

### 7.2 進行外部查證（由 Agent 執行）

建議三輪：

1. 官方與一手來源
2. 主流媒體交叉
3. 反證與闢謠

把查到的 evidence 整理成 JSON 後交給 score。

### 7.3 內部評分

```bash
python3 scripts/factcheck_engine.py score \
  --input evidence.json \
  --output scored.json
```

### 7.4 產生使用者回覆

```bash
python3 scripts/factcheck_engine.py compose \
  --input scored.json \
  --output reply.txt
```

## 8. 輸入與輸出資料格式

### 8.1 score 輸入（evidence.json）

每個 claim 可包含：

- `claim`
- `type`
- `evidence.official_count`
- `evidence.mainstream_count`
- `evidence.independent_count`
- `evidence.factcheck_true`
- `evidence.factcheck_false`
- `evidence.authority_rebuttal`
- `evidence.outdated_presented_current`
- `evidence.source_chain_hops`
- `evidence.core_contradiction`
- `evidence.has_timestamp`
- `evidence.strong_social_debunk`
- `evidence.out_of_context`
- `evidence.headline_mismatch`
- `evidence.missing_data_citation`
- `evidence.fact_opinion_mixed`

### 8.2 compose 輸入（scored.json）

- `band` 由 score 輸出：`true|false|uncertain|prediction|opinion|satire`
- `findings`、`correct_info`、`sources` 可由 Agent 補齊

## 9. 判定策略（對外不顯示分數）

- `true`：回覆「查核後屬實」，可延伸背景但須準確。
- `false`：回覆「與資料不符」，直接整合正確資訊。
- `uncertain`：回覆「目前無法確認」，說明現況。
- `prediction`：不做真偽裁定，只提供查詢到的預測資訊。
- `opinion`：回覆為觀點陳述，非事實查核對象。
- `satire`：回覆為諷刺/虛構來源。

## 10. 回覆風格規範

- 不顯示內部分數。
- 不分離「補充」「正確資訊」段落，直接整合進自然敘述。
- 非必要不條列。
- 優先呈現錯誤訊息，再呈現存疑，最後是正確訊息。
- 來源使用可點擊超連結。

## 11. 限制與風險

- 付費牆與未公開資料不可見。
- 即時事件可能在數分鐘內變化。
- 社群平台訊號不可當主證據。
- 某些國家官方資料可能存在立場偏差，需交叉驗證。

## 12. 多語文件

- 英文：`docs/README.en.md`
- 西班牙文：`docs/README.es.md`
- 阿拉伯文：`docs/README.ar.md`
