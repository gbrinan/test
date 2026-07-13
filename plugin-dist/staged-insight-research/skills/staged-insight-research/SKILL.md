---
name: staged-insight-research
description: Staged consumer/user research pipeline — phase 1 broad survey → phase 2 extended validation → phase 3 focus interview — designed backward from a single GOAL via the GOAL→KNOWLEDGE→SEGMENT→QUESTION framework, with every phase persisted to a project directory (manifest.json + phase files + summary.md) so later sessions and other agents can resume or consume the findings. TRIGGER when the user asks for multi-stage consumer research, a research project with saved intermediate results, "1차 조사/2차 확장/포커스 인터뷰", designing an interview or survey guide from a business goal, converting a flat questionnaire into an insight-driven one, or resuming a research project that has a manifest.json.
---

# Staged Insight Research

A research project is not a questionnaire — it is a **decision waiting for evidence**. This skill runs a three-phase pipeline that accumulates evidence into a project directory any agent can pick up later.

## Design philosophy — guardrails, not scripts

Rules tagged [HARD] are mandatory. Everything else is executor judgment ([FREE]): merge phases, resize samples, change question styles freely — but record the reasoning in the manifest `note`.

## [HARD] Storage convention — the reason this skill exists

All artifacts live in one project directory (default root `research/` under the current project; caller may override):

```
research/{project-id}/
├── manifest.json      ← single source of truth for project state
├── phase1-broad.md
├── phase2-extended.md
├── phase3-focus.md
├── summary.md         ← the default entry point for downstream work
└── raw/               ← (optional) per-respondent replies, batch files
```

- `project-id`: kebab-case slug (e.g. `ai-parenting-channel-2607`)
- **On start**: if `manifest.json` exists, Read it and resume; otherwise create it
- **On phase completion**: save the phase file AND update the phase status in the manifest — never skip either
- **On project completion**: write `summary.md` so downstream consumers need to read only that file

### manifest.json schema

```json
{
  "project_id": "ai-parenting-channel-2607",
  "goal": "one-sentence decision this research must enable",
  "created": "YYYY-MM-DD",
  "updated": "YYYY-MM-DD",
  "phases": {
    "phase1": { "status": "done|in-progress|pending|skipped", "file": "phase1-broad.md", "date": "", "note": "judgment memo (merge/skip/sample-size reasoning)" },
    "phase2": { "status": "pending", "file": "phase2-extended.md", "date": "", "note": "" },
    "phase3": { "status": "pending", "file": "phase3-focus.md", "date": "", "note": "" }
  },
  "summary_file": "summary.md",
  "external_data": [],
  "downstream_hints": ["what later work should consume this (e.g. campaign brief, landing copy)"]
}
```

## [HARD] Reverse-design frame — GOAL → KNOWLEDGE → SEGMENT → QUESTION

Before writing any question, in any phase:

1. **GOAL** — one sentence: what decision/deliverable must this research enable?
2. **KNOWLEDGE (K1..Kn)** — the knowledge items the GOAL requires, each annotated with *who holds it* (which segment can answer)
3. **SEGMENT** — a priority table of respondents who can answer each K. Demographics are a *proxy* for K-ownership, never the goal itself
4. **QUESTION** — every question carries a K-tag and a stated *output use* (headline copy, channel concept, segment priority, offer design…). Never reuse a blunt multiple-choice/abstract original question as-is — convert it into one that probes a **lived, specific moment plus the self-talk in that moment**

## The three phases ([FREE] — details are judgment)

### Phase 1 — Broad → `phase1-broad.md`
Map the terrain per K; find where segments diverge. Structured instruments (Likert, ranking, multi-choice), roughly 10–30 respondents per segment, scaled to GOAL stakes. Output: per-K distributions, segment comparison, candidate axes for phase 2.

### Phase 2 — Extended → `phase2-extended.md`
Widen and re-test the axes that diverged in phase 1; collect counter-cases. Re-test surprising phase-1 findings with a larger N before believing them — small-N artifacts are common (a 0% finding at N=12 can become 20% at N=30). May shrink or skip if phase 1 was decisive (record why). Output: confirmed segments, verified/killed hypotheses, focus-interview candidates.

### Phase 3 — Focus interview → `phase3-focus.md`
4–6 core respondents, depth interview. Default structure (experience research): screener → warm-up → elicit definitions → **critical-experience reconstruction** (place, counterpart, trigger, the decisive moment, before/after shift — down to remembered lines of dialogue) → counter-case → operational variables → revisit/referral triggers → closing. For copy/offer design GOALs, substitute the pain → desire → objection-demolition → success-criteria (floor/ceiling) block structure.

Two execution modes — pick per respondent, mixing is fine:

- **Batch mode** (default for coverage): dispatch the interview guide through the `persona-respondent` sub-agent, one persona per dispatch (interview-depth work needs the strongest character fidelity — do NOT batch multiple personas per dispatch in phase 3).
- **Interactive mode** (default when a human wants to probe live): hand the session to the `nemotron-personas-korea:persona-interviewee` skill **as-is** — Claude plays one specific persona in-character, the user interviews directly, bracketed `[...]` text is out-of-character stage direction. Use this for A/B reaction probes (e.g. showing two DM drafts and digging into which lands and why), for follow-up chains a fixed guide can't anticipate, and whenever the requester says they want to "talk to" a respondent. Afterwards, transcribe the exchange into `phase3-focus.md` (or `raw/interview-{n}.md` + a digest) so the project directory — not the chat log — remains the record.

### Summary → `summary.md`
Written so downstream work reads only this: GOAL + final recommendation, per-K findings (≤3 lines each, linked to phase files), top 5–10 quotable raw sentences, downstream suggestions.

## Respondent sources ([FREE])

- If the `nemotron-personas-korea` plugin is installed, use its skills: `dataset` (schema/sampling), `dispatch-strategy` (parallel dispatch), `persona-respondent` sub-agent (replies), `bulk-reply-save` (persisting ≥3 reply files), `synthetic-population-validity` (checking synthetic answers against real-population marginals). Prefer reading an already-downloaded local parquet copy over re-downloading through the `datasets` library (which builds a separate, ~3× larger Arrow cache).
- Otherwise: design contrasting virtual personas by hand, or use real-respondent data if provided.
- [HARD] Any synthetic-persona result must carry the disclaimer:
  `※ 본 결과는 가상 페르소나 시뮬레이션입니다. 실제 사용자 검증을 대체하지 않습니다.`

## [HARD] External data integration — when real data arrives

Synthetic findings are provisional. Whenever external data lands (a real field survey, VOC, interview transcripts, sales stats — at any time, even after the project is closed):

1. Store the raw file(s) under `external-data/` inside the project directory, never inline in phase files.
2. Append an entry to `external_data` in the manifest:
   ```json
   "external_data": [
     { "file": "external-data/field-survey-0815.xlsx", "received": "YYYY-MM-DD",
       "scope": "which Ks / claims it bears on", "integrated": false, "note": "" }
   ]
   ```
3. **Compare before overwriting**: check each affected synthetic finding against the real data (the `synthetic-population-validity` skill has the statistics for marginal/shape/joint comparison and for judging whether a gap is real signal or sampling noise). Classify each finding: `confirmed` / `corrected` / `overturned` / `not-covered`.
4. Amend the affected phase files **additively** — add a `## 외부 데이터 검증 (YYYY-MM-DD)` section stating the verdicts; do not silently rewrite original synthetic conclusions (the audit trail is the point).
5. Rewrite `summary.md` conclusions where verdicts demand it, bump the changelog (`## 개정 이력`), and flip `integrated: true`.
6. Findings confirmed by real data may drop the synthetic-simulation disclaimer **for those claims only**; everything else keeps it.

## [HARD] Quality gates

- In any simulated interview, personas must visibly disagree somewhere — unanimous opinion means the simulation failed; redo it.
- Every phase file opens with a header: GOAL, target Ks, respondent count, method summary (so a consumer can read it without context).
- Any merged/skipped phase records its reasoning in the manifest `note`.
- One writer per project-id at a time — if another agent/session is mid-write on the same project, coordinate before touching the manifest.
