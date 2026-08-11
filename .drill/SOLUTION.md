# Brownfield Live Rep — Answer Key (EXAMINER ONLY)

Do not surface this file until debrief. Do not hint at it during the session.

Product name in-repo: **FieldTrack**
Layout: `backend/` (FastAPI), `web/` (Next.js App Router), `tests/` (happy paths only)

---

## Phase 1 — Security (planted)

### Tier 1 — backend (all five)

| # | Pattern | Location | Confirm |
|---|---------|----------|---------|
| 1 | **Missing ownership check (IDOR)** | `backend/routers/tickets.py` `get_ticket`, `update_ticket` | User A reads/patches User B's ticket by id |
| 2 | **Missing auth dependency** | `backend/routers/comments.py` `delete_comment` | Unauthenticated `DELETE` removes a comment |
| 3 | **Mass-assignment schema** | `backend/schemas.py` `UserProfile` + `backend/routers/users.py` `update_me` | `PATCH /users/me` with `{"is_admin": true}` |
| 4 | **Blocking call in `async def`** | `backend/routers/users.py` `dispatch_webhook` | `time.sleep` + sync `requests.post` inside `async def` |
| 5 | **CORS `*` + credentials** | `backend/main.py` | `allow_origins=["*"]` with `allow_credentials=True` |

### Tier 1b — frontend (planted; use 2–3 in session)

| # | Pattern | Location |
|---|---------|----------|
| 1 | **Client-side-only authorization** | `web/components/TicketAdminActions.tsx` — button hidden if `!user.isAdmin`; endpoint not gated |
| 2 | **`app/api/` route skips backend check** | `web/app/api/tickets/[id]/force-close/route.ts` — no authz; soft-fails to `{ok: true}` |
| 3 | **Token / secret stored wrong** | `web/lib/auth.ts` + `web/app/login/page.tsx` — bearer in `localStorage`; `NEXT_PUBLIC_ANALYTICS_WRITE_KEY` in `web/.env.local` / `web/lib/api.ts` |

Bonus / browse (not required for phase openers):
- `dangerouslySetInnerHTML` — `web/components/CommentThread.tsx`
- SC over-fetch → CC — `web/app/settings/page.tsx` → `SettingsPanel`
- JWT `verify_signature=False` — `backend/deps.py` `get_current_user` (contrast: `get_optional_user` is correct)
- SQL injection f-string — `tickets_by_status`
- Plaintext password `==` + stack leak — `backend/routers/auth.py` `login`

### Clean / false-positive bait (phase 1)

- `search_tickets` — raw SQL string but **parameterized** (`:owner_id`, `:pattern`)
- `list_comments` / `create_comment` — ownership checked correctly
- `list_tickets` — filters by `owner_id` (contrast with get/update)
- `/health`, `web/app/api/health/route.ts`, landing page — public by design
- Tickets SSR cookie path (`ft_session`) — correct contrast to `localStorage` login

---

## Phase 2 — Data correctness (planted)

| # | Bug | Location | Symptom |
|---|-----|----------|---------|
| 1 | **Lost-update / last-write-wins** | `Ticket.version` exists; `update_ticket` pops `expected_version` and never increments/compares | Concurrent PATCHes silently overwrite |
| 2 | **Non-idempotent POST** | `create_ticket` accepts `Idempotency-Key` header and ignores it; `CreateTicketForm` sends no key | Flaky-network retry → duplicate tickets |
| 3 | **N+1 query** | `list_tickets` loops: per-ticket `Comment.count()` + `User` lookup | List endpoint scales with 2N+1 queries |
| 4 | **Missing transaction** | `close_ticket` — separate `db.commit()` for status then activity | Partial failure leaves closed ticket with no audit row |

Tests trap: `tests/test_happy_paths.py` covers single-writer create/update/close only. Passing suite proves nothing about races, retries, or authz.

### Clean / false-positive bait (phase 2)

- `Ticket.version` field presence alone is not a fix — writers ignore it
- `onupdate=datetime.utcnow` on `updated_at` is fine; not concurrency control
- Search parameterized SQL looks "raw" but is safe

---

## Phase 3 — Architecture (planted seams)

| # | Seam | Location | Why it bites a second client / load |
|---|------|----------|-------------------------------------|
| 1 | **Business logic in route handler** | `_apply_sla_and_transitions` inside `backend/routers/tickets.py` | Status machine + SLA escalation + urgent title tagging only exist on this HTTP path; mobile must duplicate or call web-shaped APIs |
| 2 | **Cache with no invalidation** | `backend/cache.py` + `get_ticket` puts / `update_ticket` never clears | Stale reads under load after writes; worse with multi-worker (per-process cache) |
| 3 | **Second-client cost in data layer** | `backend/db.py` `ticket_to_client_payload` + `GET /tickets/{id}/client-view` | `rendered_html` / `web_nav` baked into shared payload — mobile pays for web chrome |

Strong answer names a **concrete seam** (e.g. extract domain service for transitions; invalidate/remove process cache; split presentation DTOs from domain) and a **consequence** (divergent rules across clients, stale ticket views, payload bloat).

### Clean / false-positive bait (phase 3)

- "Add Redis" without invalidation story — repeats the planted cache bug at larger scale
- "Just use microservices" — not grounded in a seam visible in this repo
- Separating `TicketCreate` / `TicketOut` schemas is already fine — not the seam

---

## Session openers (verbatim targets)

**Phase 1:** report that a user may have seen another user's ticket → IDOR on get/update is the narrative hook; other Tier-1/1b findings are fair game if he leads there.

**Phase 2:** duplicate tickets on flaky network + concurrent edit overwrite → idempotency + lost-update; N+1 and missing txn are available if he digs.

**Phase 3:** second client (mobile) + growth → service-layer / cache invalidation / web-coupled payload.

---

## Tracking checklist (fill during live; write `LIVE_REPORT.md` at debrief)

Per phase: clarifying Q before dive? narrated before agent output? impact + confirm step? verified vs face-value? failing test requested? bare approvals? caught planted FP?

---

## Grading note

If he says "tests pass so we're fine" → miss. Bonus if he asks for a failing authz / idempotency / concurrency test before claiming a fix.
