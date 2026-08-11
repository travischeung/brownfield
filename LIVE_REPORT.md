# FieldTrack Brownfield Live Rep — Session Report

**Candidate session date:** 2026-08-11  
**Product:** FieldTrack (FastAPI + Next.js drill repo)  
**Format:** Dual-role interviewer + coding agent  

---

## Overall outcome

| Phase | Theme | Result |
|-------|--------|--------|
| **1 — Security** | Cross-user ticket visibility | **Primary finding hit** (IDOR on by-id get/update). Spent too long on entry-path / provenance. Adjacent findings noted unevenly. |
| **2 — Data correctness** | Duplicates + lost concurrent edits | **Both primary themes addressed and implemented** (idempotency MVP + optimistic locking). Verified with smokes/tests. |
| **3 — Architecture** | Second client (mobile) + scale | **Strong seams named** (cache invalidation → fixed; web-coupled `client-view` / `ticket_to_client_payload`; domain rules in PATCH router). Early monorepo-split idea was weak; corrected toward API seams. |

**Verdict:** Passable-to-strong on finding and fixing once scoped; Phase 1 process was the weak spot (closure / rabbit holes / late AI reliance). Phases 2–3 showed clearer candidate-led design → implement → verify.

---

## Phase-by-phase: what you did

### Phase 1 — Security

**Scenario:** User reported briefly seeing another user’s ticket; suite green.

**What went well**
- Started with CORS smell, then tickets with an IDOR lens — correct instinct for the narrative hook.
- Contrasted list/search/create (owner-scoped) vs by-id get/update (no ownership).
- Clarifying questions to “support”; distinguished list vs detail; used curl/API confirm when UI failed on comments.
- Documented findings with TODOs rather than silent drive-by fixes.
- Eventually closed with a solid impact statement (IDOR on get vs list; confirm via curl).

**What hurt**
- Over-invested in **how the foreign id entered** (cache TTL, Next cache, A+B list mix, JWT-as-everyone). Entry path is optional; the defect was enough to move on.
- Late Phase 1 prompts shifted to “what did I miss / likely culprits” after the hypothesis list ran dry — agent-led gap analysis.
- UI repro on `/tickets/{foreign}` correctly hit comments ownership asymmetry; interpreted as confusion before treating API GET as the confirm layer.

**Parked / adjacent (seen but not fully closed as Phase 1 punch list)**
- CORS `*` + credentials  
- Mass-assignment `is_admin` on `PATCH /users/me`  
- JWT `verify_signature=False`  
- Stale cache (later fixed in Phase 3)  
- Admin-by-status / SQLi (deprioritized for this reporter)

**Fixes in Phase 1:** Comment/TODOs only (IDOR, cache notes) — appropriate; no requirement to patch authz before Phase 2.

---

### Phase 2 — Data correctness

**Scenario:** Duplicate creates on flaky network; concurrent edits both “succeed” with lost data.

**What went well**
- Idempotency: correct mental model; confirmed header accepted-and-ignored + client sent nothing.
- Asked blast-radius before implement — good interview habit.
- Implemented Ticket-column MVP (`UniqueConstraint(owner_id, idempotency_key)`), client UUID header, regression test.
- Lost updates: self-corrected cache hypothesis toward missing optimistic concurrency; narrated `expected_version` pop clearly.
- Implemented compare → 409 / bump `version`; conflict test + curl smokes with explicit expected outcomes.

**Gaps (available in key, not required once primaries landed)**
- N+1 on `list_tickets`  
- Split commits on `close_ticket` (missing single transaction)

**Fixes shipped**
- Idempotent create (header + DB column + client)  
- Optimistic locking on PATCH  

---

### Phase 3 — Architecture

**Scenario:** Mobile second client + higher traffic.

**What went well**
- Clarified JWT works for mobile (bearer + secure store); web `localStorage` is client-specific.
- Linked Phase 2 idempotency to flaky mobile networks — good cross-phase judgment.
- Named cache invalidation as scale/multi-client seam; implemented write-aside invalidate on PATCH/close + test.
- Identified web-coupled payload (`client-view` / `ticket_to_client_payload` with `rendered_html` / `web_nav`) and domain rules trapped in `_apply_sla_and_transitions` on PATCH.

**Weaker start**
- Leading with monorepo split (web / mobile / backend) without a code seam — packaging ≠ architecture fix.
- Treating “Next is irrelevant so API is fine” until pushed to look at backend presentation/logic coupling.

**Fixes shipped**
- Cache write-aside invalidation  

**Characterized, not necessarily fully refactored**
- Decouple presentation from data layer  
- Extract domain/service for SLA/transitions  

---

## AI query patterns — what you asked and how appropriate

Scale: **Appropriate** | **Borderline** | **Weak for interview**

### Appropriate (do more of this)

| Kind of ask | Example from session | Why it works |
|-------------|----------------------|--------------|
| Hypothesis → scoped read | “Confirm cache hit has no ownership check” | You lead; agent verifies |
| Blast radius before build | “Nullable unique `(owner_id, idempotency_key)` — blast-radius call sites; I’ll decide” | Impact analysis you own |
| Spec’d implement | “Check `expected_version` before commit; mismatch → fail loudly” | Design stated; agent codes |
| Verify with expected outcomes | “Smoke 1: retry same key → no dupes. Smoke 2: stale PATCH → 409” | Success criteria explicit |
| Stuck protocol | “One dimension I haven’t varied (identity vs id vs role), not findings” | Asks for search space, not answers |
| Clarifying to interviewer | Push support; JWT on mobile? | Real on-call / interview behavior |
| Out-loud review (meta) | Narrating idempotency / optimistic lock without dumping to AI | Ideal IRL; typing to AI optional |

### Borderline (OK if rare / after you’ve looked)

| Kind of ask | Example | Risk |
|-------------|---------|------|
| “Which of my two hypotheses is closer?” | Cache vs locking on lost edits | Fine as **confirm** after opening PATCH; weak as first move |
| “Parse tickets.py for mobile / web-shaped endpoints” | Phase 3 list request | OK if you lack mobile background **once**; better: “I’ll scan handlers; flag web chrome / domain-in-router” |
| Env babysitting | Spin up, seed users, swallow analytics fetch | Fine for confirm once; don’t let it eat the phase |
| Meta “is this prompt OK?” | Repeated calibration | Fine in a **practice** drill; in a real interview, calibrate less and act |

### Weak (avoid in a real interview)

| Kind of ask | Example | Why it dings |
|-------------|---------|--------------|
| Open-ended gap fill | “Oversights I may have entirely missed” / “likely culprits with justification” | Hands investigation lead to the model |
| “Do another full pass and brief me” | Broad backend re-scan | Agent becomes the candidate |
| Bare “LGTM” / “looks good” with no risk points | After large implement | No verification signal |
| Fix without design | “Implement idempotency” with no shape | Better after blast-radius + chosen MVP (you did this well later) |

### Practice vs real interview

This session was a **practice drill** with heavy meta (“is this appropriate?”). In a **real** interview: say the same things **out loud** to the interviewer; use the agent for search/implement/verify with **one-sentence claims**. Don’t ask the agent to grade your prompting mid-loop.

---

## Rubric-style checklist (from drill intent)

| Signal | Phase 1 | Phase 2 | Phase 3 |
|--------|---------|---------|---------|
| Clarifying Q before deep dive | Yes (support) | Partial | Yes (JWT/mobile) |
| Narrate before agent output | Strong early; weak late | Strong | Mixed then strong |
| Impact + confirm | Eventually; delayed by entry path | Yes + smokes | Yes for cache; seams characterized |
| Verify vs face-value | Comments/UI vs API GET | Tests + curls | Cache test |
| Failing / focused test before claim fix | Not for IDOR | Yes (idempotency + conflict) | Yes (cache invalidate) |
| Bare approvals | Avoided early | Improved (named risk points) | OK |
| Caught FP / avoided rabbit hole | Struggled (list mix, Next cache) | Self-corrected cache→version | Dropped monorepo-as-fix |

---

## What to practice next

1. **Stopping rule:** After primary defect + impact + confirm plan, park provenance and move on (~15–20 min max on one rabbit hole).  
2. **Two-layer repro:** API/curl first; UI second.  
3. **One claim per agent ask:** “I expect X in file Y; confirm or deny.”  
4. **Phase 3 default:** Name a **backend** seam (rules location, DTO shape, cache) before packaging/monorepo.  
5. **Out loud > chat:** Design and review narration to interviewer; agent executes.

---

## Code changes from this session (summary)

- TODOs: IDOR, cache notes (Phase 1)  
- Idempotency: `Ticket.idempotency_key` + unique constraint; enforce on create; client header  
- Optimistic locking: require/compare `expected_version`; 409; increment `version`  
- Cache: `invalidate_cached_ticket` on PATCH and close  
- Tests: idempotency dedupe, version conflict, cache invalidate after patch  

**Not fixed (still open punch list examples):** IDOR on get/update/client-view; unsigned JWT; mass-assignment admin; comment DELETE without auth; domain logic still in router; `client-view` still web-chrome by default; N+1 list; close dual-commit; force-close without `expected_version` / authz.

---

## Bottom line

You can find and fix the **intended primary issues** when you stay hypothesis-driven and time-box. Phase 1 taught the expensive lesson: **authz hole > origin story**. Phases 2–3 showed the better loop: claim → blast radius → implement → verify with stated expects. For a real interview, keep that Phase 2/3 loop and retire the “what did I miss?” asks.
