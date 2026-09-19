# ask-ai-to-cut-30-percent-stops-at-8

**Ask an LLM to shorten a text by 20–30% and measure where it actually stops — and what it drops on the way.**
Reproduction kit for the Sumitsuke Lab article (2026-09-19): 14 Japanese service-guide pages × 4 instruction conditions = 56 shortened outputs, scored by character change, by a multiset of "number + unit" atoms, and by 29 frozen boundary sentences (conditions / limits / exceptions).

Article: [AI に「20〜30% 短くして」と頼むと中央値は −7〜−8%](https://sumitsuke.jp/lab/ask-ai-to-cut-30-percent-stops-at-8/) (Lab, Japanese)

## In one paragraph

`claude -p --model claude-opus-5` was asked, one document per call, to cut each of 14 texts (1,149–1,797 characters) by 20–30%. Four instruction conditions were nested: **0** no constraint at all; **A** keep the heading/paragraph/list structure; **B** A + keep numbers and sentences stating conditions, limits and exceptions; **C** B + lists may be converted to bullets. Median change: **0 −6.5% / A −6.9% / B −8.2% / C −8.4%**. Only **3 of 56** outputs reached −20%. The differences between conditions (≤1.3 pt) are inside the reproduction width measured beforehand (9 pilot runs, median width 6.6 pt), so the pre-registered hypotheses about the "keep" condition are HOLD; the main result is outside them — the instruction's number is not reached even with no constraints. Numbers were still dropped (27/56 outputs lost at least one "number + unit", almost always a count such as 「3 つ」; every price 「33,000 円」 survived, 18/18). Boundary sentences: 84/87 kept for A–C after human adjudication of 33 paraphrases (3 lost, all the same sentence); condition 0: 29/29 (the 9 unmatched sentences were adjudicated in one batch as paraphrases, `claims_judged_cond0_2026-09-19.csv`; note that the one sentence judged "lost" in A–C was shortened the same way in condition 0 and got "kept" there — one inconsistency in the human verdicts, left as is).

## Quick start (re-run on the same material)

Requires Python 3.10+ and the Claude Code CLI (`claude`) on PATH. Generation calls the model (paid / subscription); scoring is offline.

```bash
python t34_prepare.py            # freeze materials/ → atoms_claims_candidates.json (atoms; claims were then hand-selected into atoms_claims_frozen.json)
python t34_generate.py pilot     # 3 docs × condition A × 3 runs  → outputs/pilot/
python t34_generate.py main      # 14 docs × A/B/C, order randomized with seed 20260919 → outputs/main/
python t34_generate.py cond0     # 14 docs × condition 0 (added after review)
python t34_score.py              # → score.csv, summary.md, claims_to_judge_cond0.csv (unmatched claims for human adjudication)
```

The scripts live at the repository root and read/write `materials/`, `outputs/` and the JSON/CSV files next to them (same layout as the original evidence folder); run from a copy if you want to keep the published outputs intact. The prompts are the exact strings in `COND` (Japanese). The model is called with the text on stdin from a clean working directory (no `CLAUDE.md`); note that `claude -p` still carries Claude Code's own system prompt, so this is not a bare chat completion.

## What is measured and what is not

- **Measured**: character count without whitespace (HTML tags stripped); multiset of `number + unit` matches (`ATOM` regex in `t34_score.py`) — an atom is "lost" when it appears fewer times than in the source; boundary claims by normalized string containment (auto-pass) or human adjudication (paraphrased-kept / lost / inverted); heading and bullet counts.
- **Not measured**: text quality; other models or temperatures; a single-point target ("cut exactly 25%"); repeat runs (each cell is n=1 — the pilot shows the same input landing at −21% and −7% on different runs).

## Data

- `materials/` — the 14 source texts (see `DATA_LICENSE`: not CC BY; included for reproduction only). `materials_sha256.txt` freezes them.
- `atoms_claims_frozen.json` — 154 atoms and 29 boundary claims, frozen before generation.
- `pilot_threshold.md` — the 9 pilot runs and the HOLD threshold (6.6 pt).
- `outputs/main/<slug>__<cond>__1.md` — the 56 outputs (0/A/B/C); `outputs/pilot/` — 9 pilot outputs; `outputs/log.csv` — timestamps, seconds, character counts, exit codes; `outputs/main_order.json` — the randomized condition order; `outputs/_failed_argv_body_not_delivered/` — the first pilot attempt where the body was passed via argv and never reached the model (kept as a record).
- `score.csv` — one row per output; `summary.md` — the per-condition table; `results_summary.md` — the write-up with corrections made after external review (Japanese).
- `claims_judged_2026-09-19.csv` — the 33 A–C paraphrases with the human verdicts; `claims_judged_cond0_2026-09-19.csv` — the 9 condition-0 rows with the batch verdict.
- `SHA256SUMS` — `sha256sum -c SHA256SUMS`.

## License

Code: MIT (`LICENSE`). Data, tables and outputs: CC BY 4.0 (`DATA_LICENSE`) — please credit **Sumitsuke Lab** (https://sumitsuke.jp/lab/). `materials/` is excluded from CC BY (see `DATA_LICENSE`).
