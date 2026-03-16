# Agent Fact Check Verify

**Language Switcher**: [中文](../README.md) | **English (current)** | [Español](README.es.md) | [العربية](README.ar.md)

Version: **1.0.1**  
Author: **Allen Niu**  
License: **MIT**

`agent-fact-check-verify` is a rigorous verification skill for AI agents. It extracts verifiable claims, performs multi-source cross-checking (official, mainstream media, fact-check organizations, and social signals), applies a deterministic internal scoring policy, and produces neutral integrated user responses without exposing internal scoring details.

---

## 1. Design Goals and Professional Principles

This skill is built for auditable, reproducible verification workflows rather than “plausible sounding” summaries.

- **Reproducible**: same evidence leads to the same decision.
- **Traceable**: every conclusion maps back to source links.
- **Auditable**: fixed internal rules; no arbitrary free-form scoring.
- **Neutral phrasing**: user-facing output avoids stance-taking.
- **Bounded cost**: per-claim search budget and stop conditions.

---

## 2. Scope (What it does / does not do)

### Trigger phrases (recommended)

If user input includes “verify”, “fact-check”, “is this true”, “核實”, or “核實這個”, this skill should be selected first.

### 2.1 Included

1. Claim extraction from long text.
2. Claim type classification: statistical / causal / attribution / event / prediction / opinion / satire.
3. Three-pass verification: official-first, mainstream cross-check, counter-evidence.
4. Internal deterministic decision banding.
5. User-facing integrated response with no score disclosure.

### 2.2 Excluded

1. No hard truth judgment for pure subjective opinions.
2. No social-volume-as-truth behavior.
3. No political persuasion language.
4. No guarantee for paywalled/private/closed-source content coverage.

---

## 3. Project Structure

```text
agent-fact-check-verify/
├── SKILL.md
├── LICENSE
├── README.md                    # Chinese default
├── scripts/
│   └── factcheck_engine.py      # extract / score / compose
├── references/
│   ├── scoring-rubric.md
│   └── source-policy.md
└── docs/
    ├── README.en.md
    ├── README.es.md
    └── README.ar.md
```

---

## 4. Installation and Environment Requirements

### 4.1 Base Requirements

- Python 3.10+
- Agent search capability (Brave / Tavily / Browser)
- Read/write access to workspace

### 4.2 Quick Health Check

```bash
python3 scripts/factcheck_engine.py --help
```

If `extract|score|compose` are shown, the runtime is ready.

---

## 5. Optional CLI Tools and Cookie Categories (Important)

These CLIs are **optional**. Main flow still works without them.

- X CLI: <https://github.com/jackwener/twitter-cli>
- Reddit CLI: <https://github.com/jackwener/rdt-cli>

### 5.1 twitter-cli (Cookie-based)

Common cookie categories:

- **Required auth**: `auth_token`, `ct0`
- **Session helpers**: `guest_id`, `kdt`
- **Optional fields**: `twid`, `lang`

Operational recommendations:

- Store cookie files locally with restricted permissions.
- Never commit cookies to git.
- Rotate cookies periodically.

### 5.2 rdt-cli (Cookie-based)

Common cookie/session categories:

- **Primary session**: `reddit_session`
- **Device/tracking**: `loid`, `session_tracker`
- **Optional auth fields**: `token_v2` (tool-version dependent)

Operational recommendations:

- Use a least-privilege account for verification workflows.
- Refresh expired cookies and avoid plaintext storage in shared systems.

---

## 6. Recommended Execution Flow

### Step A: Extract claims

```bash
python3 scripts/factcheck_engine.py extract \
  --text "input text" \
  --output claims.json
```

### Step B: Three-pass verification (agent side)

1. **Official/primary evidence first**.
2. **Mainstream independent corroboration**.
3. **Counter-evidence / debunk search**.

Recommended cap: 6 searches per claim. You may additionally run multiple X(Twitter) checks (recommended: 3 passes) as social corroboration, without changing the official/mainstream/counter-evidence search counts.

### Step C: Internal decision scoring

```bash
python3 scripts/factcheck_engine.py score \
  --input evidence.json \
  --output scored.json
```

### Step D: Compose user response

```bash
python3 scripts/factcheck_engine.py compose \
  --input scored.json \
  --output reply.txt
```

---

## 7. evidence.json Field Contract (Detailed)

Per claim recommended fields:

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

---

## 8. Hard User-facing Output Rules

- Never show internal score.
- Never expose internal scoring logic.
- Do not split into “supplement” and “correct info” sections; keep one integrated narrative.
- Avoid bullets unless necessary.
- Use clickable hyperlinks for references.
- Present in this order: false → uncertain → true.
- Always append:

`⚠️ This verification is based on publicly available information and cannot cover private or paywalled materials.`

---

## 9. Edge-case Handling

- **Prediction**: no true/false judgment; summarize available forecast sources.
- **Opinion**: mark as subjective and out of fact-check scope.
- **Satire**: mark as satirical/fictional source.
- **Insufficient evidence**: return “currently unverifiable” conservatively.

---

## 10. Risks and Limits

1. Public information is inherently incomplete.
2. Breaking stories can change quickly.
3. Social platforms are auxiliary signals, not primary evidence.
4. Institutional bias can exist even in official sources; cross-validation remains required.

---

## 11. Multilingual Documentation

- Chinese: `../README.md`
- Spanish: `README.es.md`
- Arabic: `README.ar.md`
