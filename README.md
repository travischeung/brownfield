# Round A — Agent Scale Ladder

Interview prep: prompt an agent, read real code, narrate tradeoffs, escalate scale. ~40 minutes (~10 per stage). Not graded on tests or polish.

## Skeleton

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

`GET /health` → `{"ok": true}`. Build from here in the agent.

## How to run the rep

1. Open this repo in Cursor (Agent mode). Fast model is fine.
2. Examiner opens stage 1 (see `.drill/EXAMINER.md` — do not open mid-rep if you are the candidate).
3. Each stage: product question optional → one plain prompt → predict before reading → read → one tradeoff question → escalate on a symptom.
4. After stage 4: write `.drill/ROUND_A_FULL_REP_REPORT.md`.

No prompt frameworks. No tests unless you choose to. Reason out loud about what the agent produced.
