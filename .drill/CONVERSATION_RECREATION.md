# Round A Full Rep — Full Conversation Recreation Log

**Purpose:** Recreate this practice session exactly on another device/chat.  
**Date of original session:** Wednesday, Aug 12, 2026  
**Interview target:** Ezra / Function Health  
**Repo:** `brownfield` (rewritten from stop-discipline drill into Round A Hello World skeleton)  
**Mode used:** Ask mode for interviewer/proctor; Agent mode for repo rewrite + this doc  
**Status when this log was written:** Mid Stage 2 — SQLite already applied in `app/main.py`; Stage 2 tradeoff / restatement / escalation to Stage 3 **not yet done**

---

## 0. How to recreate on another device

1. Clone/sync this repo. Ensure skeleton or current code matches the **code checkpoint** you want to resume from (see §8).
2. Install and run:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   # if using SQLAlchemy stage-2 code, also: pip install sqlalchemy
   uvicorn app.main:app --reload --port 8000
   ```
3. Open Cursor in this repo. Put the model in **Ask mode**. Paste the **bootstrap prompt** in §1.
4. Replay candidate lines from §3 onward in order. Proctor should stay in interviewer character using `.drill/EXAMINER.md`.
5. Do **not** open `.drill/EXAMINER.md` mid-rep if you are the candidate.

---

## 1. Bootstrap prompt (paste this to start the proctor)

```
You are the interviewer/proctor for Round A — Agent-in-the-Loop Scale Ladder (Ezra/Function Health prep).

Rules:
- Stay in interviewer character. When I write an agent prompt, produce/show real code (in Ask mode: paste working code in chat; in Agent mode: write files).
- Before showing code, ask what I expect it to contain.
- After I read it, ask one tradeoff question for the current scale rung.
- Escalate with a symptom, not a bare number.
- Don't volunteer tradeoffs I didn't ask about.
- No grading code elegance. Grade narration, steering, understanding.
- ~10 min per stage, 4 stages.
- Plain prompts only — no "act as senior engineer" frameworks.
- Examiner packet is .drill/EXAMINER.md — use it silently.

Domain: results-ready notification service.
Open Stage 1 with the verbatim opening from the examiner packet.
```

### Stage 1 opening (proctor says verbatim)

> We're building a **results-ready notification service** — when a member's lab or imaging results are ready, we need to tell them. This is the dead-simple MVP: a handful of users, basically just us testing it.
>
> What would you build? You can ask me anything about the product first, then write the agent a prompt.

---

## 2. Initial context that created this exercise (prior turns)

### 2a. User pasted the Round A Full Rep spec (summary)

- Purpose: stitch verbal scale-loop + real agent code gen: prompt → agent generates code → discuss tradeoffs → escalate → repeat
- Constraints: no prompt frameworks; smaller/faster model OK; not graded on tests/output quality
- Four rungs: handful → low thousands → ~100K → ~1M+
- Per stage: clarifying Q optional → one prompt → predict before reading → tradeoff Q → escalate on symptom
- Decomposition check once at stage 2 or 3
- Report to `.drill/ROUND_A_FULL_REP_REPORT.md` after stage 4
- User asked: *"take a look at this new spec. can you help me generate this practice exercise?"*

### 2b. Assistant proposed (Ask mode)

- Domain pick: notification service (later specialized for Function Health)
- Examiner packet outline, tracking sheet, escalation symptoms
- Note: then-current repo was stop-discipline (DocShare/ProfileService), not Hello World
- Asked user to switch to Agent mode to run live

### 2c. User (Agent mode)

> rewrite the repo if necessary to set up this new exercise. remember: this is interview prep. no hints in the code, no comments up front. you can select the project based on the escalation. keep in mind: this interview is for Ezra/Function Health

### 2d. Repo rewrite (what was done)

- Removed `scenario_1/`, `scenario_2/`, old stop-drill keys
- Added clean skeleton: `app/main.py` with only `GET /health`
- Added `.drill/EXAMINER.md`, `.drill/REPORT_TEMPLATE.md`
- Rewrote `README.md` for Round A
- Domain chosen: **results-ready notification service** (lab/imaging → member inbox)

### 2e. Initial Hello World skeleton (Stage 1 start state)

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
def health() -> dict:
    return {"ok": True}
```

### 2f. User

> ok. you will be the interviewer for me then. ill put u into ask mode and youll act as the proctor.

Proctor opened Stage 1.

---

## 3. Stage 1 — Full dialogue (verbatim-ish)

### Candidate — product Q1

> First question:
> - Is this fully internal? As in, is this notification serving just our lab or are we giving it to a number of different labs? Not just between brands, but locations. This will determine whether or not we should build explicitly for scaling out. I understand it's for "testing" right now, but this is something that shapes architecture decisions even now.

### Proctor

> For this MVP it's **our** product and **our** members — one deployment, not a multi-lab SaaS you're selling to other labs or locations.
>
> If we later need per-lab isolation, that's a later conversation. Don't architect for every location as a tenant unless you have a concrete reason to assume that now.
>
> Anything else, or ready to write the prompt?

### Candidate — product Q2

> Got it. This is a "MVP/demo" type situation that we're getting working for testing/demo purposes.
>
> My understanding is that the services we're listening to will tell our service, and then our service will notify the clients that are registered. Do we need to persist the notification log for observability? In other words, is there reviewing recent notifications/etc?

### Proctor

> For MVP: yes on a simple member-facing inbox — they should be able to see recent "results ready" notices for themselves.
>
> No on a full ops/audit notification log for reviewing sends across the system. That's not a requirement for this testing slice.
>
> Anything else, or write the prompt?

### Candidate — product Q3

> Are we using any kinds of third party notification services? Twillio, etc.? Is the notification going out as push, text, email, etc

### Proctor

> In-app only for this MVP — show it in the member's inbox. No Twilio, push, SMS, or email yet.
>
> Write the prompt when you're ready.

### Candidate — product Q4

> A scoping clarification for the domain: what is the method of showing it in the inbox? If its an internal tool, we can push to a downstream endpoint.

### Proctor

> Keep it pull for the MVP: this service stores the notice and exposes an API the client (web/mobile) calls to load the member's inbox. Don't push to a separate downstream notification endpoint yet.
>
> Ready for the prompt when you are.

### Candidate — approach narration (not yet a prompt)

> So here's my overall thoughts/approach on prompt:
> I will design a notification service that relies on external (upstream) services subscribing to our service. Once registered, we'll give the upstream service an endpoint that they can invoke when they finish their jobs and are ready to notify their users. The service is purely for MVP purposes, so I am comfortable with the logs of most-recent-notif per service to be held simply in memory, no external DBs. The service will update the downstream users with a simple polling/pull, meaning that we can simply design this as a GET FastAPI endpoint.
>
> Out of scope: Message queues for high throughput on incoming requests, external DBs (SQLite was another potential candidate, but it's overkill if we're just demoing with a handful of features), user-groups for who gets notified to each registered upstream service (we can just blast to everyone for this smaller demo), email/text/push

### Proctor

> One product correction: don't blast everyone. Each notice is for a **specific member** — they only see their own inbox.
>
> Upstream calling you when a result is ready is fine; for MVP that can just be a create endpoint (no separate "register upstream services" flow unless you want it).
>
> Write the actual prompt when ready — plain and direct.

### Candidate

> ok, so instead of a blast, the service can simply register the allowed/target user_id for the polling/pull

### Proctor

> Right idea: each notice is addressed to a `member_id` (or `user_id`), and the inbox GET only returns that member's items. You don't need a separate "register allowed users" step for MVP — the create payload carries who it's for.
>
> Drop the prompt when ready.

---

## 4. Stage 1 — Agent prompts and coaching

### Candidate — Prompt A (heavy / framework-ish) — DO NOT reuse; this was coached away

```
Context: I am building out a notification service that clients will consume via polling. The service will have a registration endpoint that adds producers and their desired user_id notification targets. The producers and targets will be stored in memory because the scale of the application is only a handful of internal users for an MVP/testing. Once registered, we will return an endpoint that the producer can invoke when they are ready to notify their users. The payload will include the notification text. The service is purely for MVP purposes, so the logs of most-recent-notif per service can also be held simply in memory, no external DBs. The service will update the downstream users with a simple polling/pull, meaning that we can simply design this as a GET FastAPI endpoint. 

Out of scope: message queues, external DBs, email/push/text notification

Your task is to create these two simple endpoints and local memory store. Before implementing, repeat to me your understanding of the task and ask questions on details where necessary.
```

### Proctor (before showing code)

> Before I show what the agent produces — what do you expect this code to contain? Walk me through the shape: endpoints, payloads, what lives in memory.

### Candidate

> well first, just tell me if this is an appropriate form of a prompt

### Proctor — prompt form feedback

> Form-wise: **too heavy for this round.**
>
> What's working: clear MVP constraints (in-memory, poll/GET, no queues/email).
>
> What drifts from the brief:
> - Essay "Context / Out of scope / Your task" scaffolding
> - Asking the agent to restate understanding and ask questions before coding — that burns clock and isn't how you'd prompt under time pressure
> - Speccing a producer **registration** flow that returns a dedicated notify URL — more product surface than you need after we already said create + per-member inbox GET
>
> A plain version would look more like: extend `app/main.py` with POST to create a notification for a `member_id` (message + optional `result_id`) and GET to list that member's notifications; in-memory list/dict is fine.
>
> Want to rewrite the prompt shorter, or stick with this one and keep going?

### Candidate

> what is a better format? I've been holding the understanding that i need a context, oos, task, and verification of understanding phase

### Proctor — plain prompt philosophy (KEEP THIS)

> That format is useful for long agent sessions. **This round grades against it.**
>
> The brief wants a prompt that looks like something you'd type in 20 seconds under pressure: **what to build, where, what's enough.** Not a mini-PRD and not a ceremony with the model.
>
> Drop these by default:
> - "Context:" / "Out of scope:" / "Your task:" labels
> - "Restate your understanding and ask questions before coding"
> - Role scaffolding ("act as a senior…")
>
> Keep only what changes the code:
> - File or app to touch
> - Endpoints + fields
> - Storage assumption if it matters ("in-memory is fine")
> - One hard "don't" if it prevents a rabbit hole ("no DB, no email")
>
> **Better shape (plain):**
>
> > In `app/main.py`, add POST `/notifications` that accepts `member_id`, `result_id`, and `message` and stores them in memory. Add GET `/notifications/{member_id}` that returns that member's notifications newest-first. Keep `/health`. No database, no queues, no email.
>
> That's the whole prompt. Clarifying questions happen with **me** (product), not as a phase you force on the agent.
>
> Verification of understanding is **you** predicting what the code will contain after you send the prompt — which is the step we're already on.

### Candidate — Prompt B (plain) — USE THIS FOR STAGE 1 RECREATE

```
In app/main.py, add POST /notifications that accepts member_id, result_id, and message and stores them in memory. Add GET /notifications/{member_id} that returns that member's notifications newest-first. Keep /health. No database, no queues, no email.
```

Candidate then said they used that format, smoke-tested, asked for next phase.

### Stage 1 agent output (in-memory) — checkpoint after Prompt B

```python
from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# In-memory storage for notifications
notifications: dict[str, list[dict]] = {}


class NotificationRequest(BaseModel):
    member_id: str
    result_id: str
    message: str


@app.post("/notifications")
def create_notification(notification: NotificationRequest) -> dict:
    member_id = notification.member_id
    
    if member_id not in notifications:
        notifications[member_id] = []
    
    notification_data = {
        "member_id": member_id,
        "result_id": notification.result_id,
        "message": notification.message,
        "created_at": datetime.utcnow().isoformat(),
    }
    
    notifications[member_id].append(notification_data)
    return notification_data


@app.get("/notifications/{member_id}")
def get_notifications(member_id: str) -> dict:
    member_notifications = notifications.get(member_id, [])
    # Sort by created_at descending (newest first)
    sorted_notifications = sorted(
        member_notifications, key=lambda x: x["created_at"], reverse=True
    )
    return {"member_id": member_id, "notifications": sorted_notifications}


@app.get("/health")
def health() -> dict:
    return {"ok": True}
```

### Proctor review + Stage 1 tradeoff

> **Prompt philosophy (use this going forward)**  
> Ask for a **code change**, not a briefing. One breath: where → what endpoints/fields → what's "enough" → one hard don't if it blocks a rabbit hole. Clarifying questions go to the interviewer; prediction/verification is *you* narrating before/after the agent runs — not a phase you assign to the model.
>
> **What you got**  
> In-memory `dict[member_id → list]`, `POST /notifications` with `member_id` / `result_id` / `message` + timestamp, `GET /notifications/{member_id}` newest-first, `/health` kept. Matches the plain prompt. Fine for a handful of users.
>
> Before the tradeoff: in your own words, what did we just ship?
>
> Then answer this: **You chose process memory for the inbox. What breaks first if this jumps to a few thousand members hitting it at once?**

### Candidate — restatement + tradeoff answer

> here's what i'd say to the interviewer when reviewing what came out.
>
> in this code, we're using a simple in-memory storage for notifs. reasoning is that we don't need to spin up any external DB at this stage since we're only creating an MVP that services a handful of users. its kept barebones on purpose. should we see a jump to a few thousand members, we can run into the issue of running out of storage or getting lagged out or possibly even collisions. if it crashes, everything is gone. utterly ephemeral. no acid.

### Proctor feedback + escalate to Stage 2

> Strongest part of that answer: **restart/deploy wipes the inbox** — concrete mechanism, concrete consequence. Hold that shape.
>
> Weaker: "storage / lag / collisions / no ACID" without saying *what* fails first. At a few thousand, you're not usually OOM or hashing collisions first — you're losing data the moment the process dies or you run more than one worker with separate memory.
>
> ---
>
> Support says members are losing "results ready" notifications after deploys and restarts. We're at low thousands of members now.
>
> What changes? Product question first if you need one, otherwise one plain prompt.

---

## 5. Stage 2 — Dialogue so far

### Candidate

> clearly, the in memory store is beginning to reach its limits on deploys and restarts, a tradeoff we understood during MVP/demo/testing. at this point, i would consider running it with a very light DB, the records are still insanely small, so a few thousand users is not a big deal. i would use a sqlite DB at this point to persist messages even in the case that a redeployment or restart occurs

### Proctor

> Reasonable call for this rung.
>
> Write one plain prompt for the agent. Same philosophy: where → what changes → enough → one hard don't if needed.

### Candidate — meta

> do i need to spin up a db myself here for real? can i do that irl thru cursor ai

### Proctor

> For this rung you don't spin up a database *server*. SQLite is a file (e.g. `notifications.db`) the app opens itself.
>
> In Cursor Agent mode, yes — you prompt it to switch storage to SQLite; it writes the code, creates/opens the file on first request. You don't manually provision anything beyond having Python deps installed.
>
> In this Ask-mode proctor chat I won't edit the repo; either paste the plain prompt here and I'll show the code in chat for review, or flip to Agent mode in another chat to apply it for real and smoke-test.
>
> Either way: drop the plain prompt when ready.

### Candidate — Prompt C (draft) + theory Q

> prompt:
> Remove the in-memory storage of notifications in /main replace our memory solution with a new db for SQLite db. Keep the same structure as the in-memory store in terms of key/value.
>
> how's the prompt?
>
> theory question: how does SQLite handle restarts and ACID principles if its just in the repo as a file. is it essentially a giant json-ish file that can be queried w SQL and redeploys alongside the app on restarts. persistence happens bc its literally saved into the file?

### Proctor — prompt tighten + theory

**Prompt feedback:** Directionally right, a bit imprecise.
- Path: `app/main.py` (not `/main`)
- Don't ask to "keep key/value structure" — SQLite is relational. Ask to keep the same HTTP API and persist rows
- Optional: create table on startup; db file e.g. `notifications.db`

**Tightened Prompt D (recommended Stage 2 prompt):**

```
In app/main.py, replace the in-memory notifications dict with SQLite. Keep POST /notifications and GET /notifications/{member_id} behavior the same. Store rows in notifications.db, create the table if needed. No other features.
```

**Theory answer (keep):**
- Persistence is "on disk," yes — but **not** a giant JSON file
- SQLite = binary DB file (B-tree pages, indexes, journal/WAL); SQL API
- Restarts: same file still on disk → data remains
- ACID: transactions for A/C/I; durability via flush/fsync on commit
- Deploy gotcha: if container filesystem is wiped and db isn't on a **volume**, you still lose data

### Candidate then applied SQLite (Agent elsewhere) — current repo state is Stage 2 code (see §8)

---

## 6. Examiner silent answers (product) — for proctor recreate

| Topic | Answer used |
|-------|-------------|
| Multi-lab / multi-location tenants | No — our product, our members, one deployment |
| Ops audit log | No for MVP |
| Member inbox of recent notices | Yes |
| Channels | In-app only; no Twilio/email/SMS/push |
| Delivery to client | Pull/GET inbox API, not push to downstream |
| Blast everyone | No — per `member_id` |
| Separate producer registration | Not required; create payload carries target |
| Payload | `member_id`, `result_id`, `message` |

### Planned escalations (not yet delivered in this session)

**→ Stage 3 (~100K):**  
> Mobile and web both need the inbox; email is on the roadmap. Latency spikes when a large cohort gets results the same morning. We're around 100K members.

**→ Stage 4 (~1M+):**  
> Ops sees retry storms after a partial outage — some members got the same "results ready" alert three times, others got nothing. We're past a million.

### Planned tradeoffs remaining

- **S2 (do next):** Why persist first vs putting a queue in front of the sender? / What did you just implicitly decide about delivery guarantees that you didn't say out loud?
- **S3:** What breaks first on a morning fan-out to 50K members with the shape you just shipped?
- **S4:** Idempotency key vs at-most-once drop — which did the agent effectively choose, and what concrete failure does that create at this scale?
- **Decomposition (once, S2 or S3):** If you only had time to build one more thing before this ships, what would you build and what would you explicitly defer?

---

## 7. Tracking notes so far (partial report seed)

### Stage 1 — handful
- Clarifying Q before prompt: **yes** (several)
- Prompt style: started framework-ish (Prompt A), corrected to **plain** (Prompt B)
- Predicted before reading: **partial** (asked about prompt form first; smoke-tested before formal predict-in-chat)
- Restated in own words: **yes**
- Tradeoff: mixed — strong on ephemeral/restart wipe; buzzwordy on storage/lag/collisions/ACID
- Complexity/perf unprompted: **partial** (named crash/ephemeral)

### Stage 2 — low thousands
- Approach: SQLite — **stated**
- Prompt: draft C → tightened to D
- Theory Q on SQLite: **asked and answered**
- Code applied: **yes** (SQLAlchemy + sqlite file)
- Predict / restate / S2 tradeoff / decomposition: **NOT YET**

---

## 8. Code checkpoint NOW (resume here)

Current `app/main.py` (SQLite via SQLAlchemy) when this log was written:

```python
from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, DateTime
from sqlalchemy.orm import declarative_base, Session

app = FastAPI()

DATABASE_URL = "sqlite:///./notifications.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Base = declarative_base()


class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(String, primary_key=True, index=True)
    member_id = Column(String, index=True)
    result_id = Column(String)
    message = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)


class NotificationRequest(BaseModel):
    member_id: str
    result_id: str
    message: str


class NotificationResponse(BaseModel):
    member_id: str
    result_id: str
    message: str
    created_at: str


@app.post("/notifications")
def create_notification(notification: NotificationRequest) -> NotificationResponse:
    db = Session(engine)
    
    created_at = datetime.utcnow()
    db_notification = Notification(
        id=f"{notification.member_id}_{notification.result_id}_{int(created_at.timestamp() * 1000)}",
        member_id=notification.member_id,
        result_id=notification.result_id,
        message=notification.message,
        created_at=created_at,
    )
    
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    db.close()
    
    return NotificationResponse(
        member_id=db_notification.member_id,
        result_id=db_notification.result_id,
        message=db_notification.message,
        created_at=db_notification.created_at.isoformat(),
    )


@app.get("/notifications/{member_id}")
def get_notifications(member_id: str) -> dict:
    db = Session(engine)
    
    notifications = (
        db.query(Notification)
        .filter(Notification.member_id == member_id)
        .order_by(Notification.created_at.desc())
        .all()
    )
    
    db.close()
    
    notification_list = [
        {
            "member_id": n.member_id,
            "result_id": n.result_id,
            "message": n.message,
            "created_at": n.created_at.isoformat(),
        }
        for n in notifications
    ]
    
    return {"member_id": member_id, "notifications": notification_list}


@app.get("/health")
def health() -> dict:
    return {"ok": True}
```

Note: may need `sqlalchemy` in `requirements.txt` / venv if not already installed.

---

## 9. Resume prompt (paste on the other device to continue mid-Stage 2)

```
You are the Round A proctor (Ezra/Function Health). Continue mid Stage 2.

Repo already has SQLite persistence in app/main.py (SQLAlchemy, notifications.db). Stages 1 and early Stage 2 already happened — see .drill/CONVERSATION_RECREATION.md.

Do NOT reopen Stage 1. Next steps in order:
1. Ask me what I expected the SQLite change to contain / have me restate what we shipped in my own words.
2. Ask Stage 2 tradeoff: "Why persist first vs putting a queue in front of the sender?" or "What did you just implicitly decide about delivery guarantees that you didn't say out loud?"
3. Optionally ask the decomposition check once.
4. Escalate to Stage 3 with the symptom from .drill/EXAMINER.md.
5. Continue Stage 3–4 per the Round A protocol.
6. After Stage 4, write .drill/ROUND_A_FULL_REP_REPORT.md.

Stay in interviewer character. Plain prompts only. Don't volunteer tradeoffs.
```

---

## 10. All agent prompts in one place (canonical)

| # | Stage | Status | Prompt |
|---|-------|--------|--------|
| A | 1 | Rejected (too heavy) | See §4 Prompt A |
| B | 1 | **Used** | `In app/main.py, add POST /notifications that accepts member_id, result_id, and message and stores them in memory. Add GET /notifications/{member_id} that returns that member's notifications newest-first. Keep /health. No database, no queues, no email.` |
| C | 2 | Draft | `Remove the in-memory storage of notifications in /main replace our memory solution with a new db for SQLite db. Keep the same structure as the in-memory store in terms of key/value.` |
| D | 2 | **Recommended / applied** | `In app/main.py, replace the in-memory notifications dict with SQLite. Keep POST /notifications and GET /notifications/{member_id} behavior the same. Store rows in notifications.db, create the table if needed. No other features.` |

---

## 11. Related files

- `.drill/EXAMINER.md` — silent examiner packet
- `.drill/REPORT_TEMPLATE.md` — post-rep report shape
- `README.md` — candidate-facing Round A instructions
- `app/main.py` — live code under test
