# Agent Fact Check Verify

Version: **1.0.0**  
Author: **Allen Niu**  
License: **MIT**

This is a rigorous verification skill for AI agents. It splits input text into verifiable claims, combines official sources, mainstream media, fact-check websites, and social signals (X/Reddit), applies an internal rule-based 100-point model, and returns neutral integrated conclusions without exposing scoring details to end users.

## Table of Contents

- [1. Goal and Design Principles](#1-goal-and-design-principles)
- [2. Scope](#2-scope)
- [3. Non-functional Requirements](#3-non-functional-requirements)
- [4. Project Structure](#4-project-structure)
- [5. Installation](#5-installation)
- [6. Optional CLI Tools and Cookie Categories](#6-optional-cli-tools-and-cookie-categories)
- [7. Workflow](#7-workflow)
- [8. Input and Output Formats](#8-input-and-output-formats)
- [9. Decision Policy (No score shown to users)](#9-decision-policy-no-score-shown-to-users)
- [10. Response Style Rules](#10-response-style-rules)
- [11. Limitations and Risks](#11-limitations-and-risks)
- [12. Multilingual Docs](#12-multilingual-docs)

## 1. Goal and Design Principles

This skill focuses on truth verification and evidence traceability. It does not produce emotional framing or political persuasion.

Design principles:

1. **Reproducible**: same evidence input gives same decision.
2. **Traceable**: every conclusion links back to sources.
3. **Neutral**: user-facing wording stays neutral.
4. **Simple externally**: no internal scoring is exposed.
5. **Bounded cost**: fixed search budget per claim (recommended max: 6).

## 2. Scope

- Claim extraction from long text.
- Claim classification: statistical / causal / attribution / event / prediction / opinion / satire.
- Multi-source verification: official, mainstream, counter-evidence, social signals.
- Internal scoring: deterministic 100-point system (internal only).
- User-facing response: integrated conclusion with no score disclosure.

## 3. Non-functional Requirements

- Default user-facing language is Chinese.
- Reply order: false first, then uncertain, then true.
- Avoid bullet points unless necessary.
- Always append this disclaimer:

`⚠️ This verification is based on publicly available information and cannot cover private or paywalled materials.`

## 4. Project Structure

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

## 5. Installation

### 5.1 System Requirements

- Python 3.10+
- Agent toolchain with web search capability (Brave / Tavily / Browser)

### 5.2 Permissions

- Read/write access to workspace
- Ability to invoke search tools

### 5.3 Basic Validation

```bash
python3 scripts/factcheck_engine.py --help
```

## 6. Optional CLI Tools and Cookie Categories

These two CLIs are **optional**, not mandatory. If unavailable, fallback to normal web search.

- X search: <https://github.com/jackwener/twitter-cli>
- Reddit search: <https://github.com/jackwener/rdt-cli>

### 6.1 Common cookie categories for twitter-cli

Actual fields depend on CLI version. Common categories:

- Required: `auth_token`, `ct0`
- Common helper: `guest_id`, `kdt`
- Possibly present: `twid`, `lang`

Recommendations:

- Store cookies only in secure local environment.
- Never commit cookies to version control.

### 6.2 Common cookie/session categories for rdt-cli

Actual fields depend on CLI version. Common categories:

- Session: `reddit_session`
- Device/tracking: `loid`, `session_tracker`
- Other possible fields: `token_v2` or equivalent auth cookie

Recommendations:

- Prefer official OAuth flow if supported.
- If cookie login is required, use least-privilege account and rotate regularly.

## 7. Workflow

### 7.1 Extract claims

```bash
python3 scripts/factcheck_engine.py extract \
  --text "input text" \
  --output claims.json
```

### 7.2 External verification (agent-run)

Recommended three rounds:

1. Official and primary sources
2. Mainstream cross-check
3. Counter-evidence and debunking

Then assemble evidence JSON and run scoring.

### 7.3 Internal scoring

```bash
python3 scripts/factcheck_engine.py score \
  --input evidence.json \
  --output scored.json
```

### 7.4 Compose user response

```bash
python3 scripts/factcheck_engine.py compose \
  --input scored.json \
  --output reply.txt
```

## 8. Input and Output Formats

### 8.1 Score input (evidence.json)

Each claim can include:

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

### 8.2 Compose input (scored.json)

- `band` from score: `true|false|uncertain|prediction|opinion|satire`
- `findings`, `correct_info`, `sources` can be enriched by agent

## 9. Decision Policy (No score shown to users)

- `true`: say verified true and may extend with accurate context.
- `false`: say mismatch and directly integrate corrected information.
- `uncertain`: say currently unverifiable.
- `prediction`: no truth judgment; provide discoverable prediction sources.
- `opinion`: mark as opinion statement, not fact-check target.
- `satire`: mark as satire/fiction source.

## 10. Response Style Rules

- Do not show internal score.
- Do not split into separate “supplement” or “correct info” blocks; integrate naturally.
- Avoid bullets unless necessary.
- Show false results first, then uncertain, then true.
- Use clickable hyperlinks for sources.

## 11. Limitations and Risks

- Paywalled/private materials are not visible.
- Breaking events may change within minutes.
- Social signals are not primary evidence.
- Some official data may have institutional bias and require cross-validation.

## 12. Multilingual Docs

- Chinese: `README.md`
- Spanish: `docs/README.es.md`
- Arabic: `docs/README.ar.md`
