# Round A Examiner Packet — Function Health / Ezra

Do not open mid-rep if you are the candidate.

Interview context: health-tech (lab panels, imaging reports, member inbox). Domain chosen for PHI-adjacent delivery + fan-out + retry semantics — the same shape Function Health / Ezra care about without cloning a proprietary product.

## Domain

**Results-ready notification service** — when a member's lab panel or imaging report is ready, notify them (and later care team / multi-channel).

Opening (verbatim):

> We're building a results-ready notification service — when a member's lab or imaging results are ready, we need to tell them. This is the dead-simple MVP — a handful of users, basically just us testing it. What would you build? You can ask me anything about the product first, then write the agent a prompt.

## Product answers (if asked)

- In-app inbox is enough for MVP; email/SMS later
- No SLA yet; single region
- Payload: member id, result id, short message ("Your results are ready") — not the full clinical report
- Auth: assume a member id header for now; don't invent OAuth unless they push
- If they ask you to decide: "What would you assume, and why?"

## Silent expectations (ground the reaction — not a grading key)

| Stage | Expect produced | Often missed |
|-------|-----------------|--------------|
| 1 — handful | `POST` create notification, `GET` list by member, in-memory store | Auth depth, delivery guarantees, idempotency, PHI handling |
| 2 — low thousands | Persist across restart, basic unread/list shape | Dedup, queue vs sync, backpressure |
| 3 — ~100K | Async path, channel types, fan-out / care-team hint | Tenant isolation, DLQ, hot-member skew, observability |
| 4 — ~1M+ | Idempotency under retry, overload/drop or batching, partition hint | Exactly-once theater without naming duplicate-send failure |

## Escalation symptoms

**→ Stage 2 (low thousands)**  
> Support says members are losing "results ready" notifications after deploys and restarts. We're at low thousands of members now.

**→ Stage 3 (~100K)**  
> Mobile and web both need the inbox; email is on the roadmap. Latency spikes when a large cohort gets results the same morning. We're around 100K members.

**→ Stage 4 (~1M+)**  
> Ops sees retry storms after a partial outage — some members got the same "results ready" alert three times, others got nothing. We're past a million.

## Tradeoff questions (one per stage)

- **S1:** You just chose in-memory storage. What breaks first if this jumps to a few thousand members hitting it at once?
- **S2:** Why persist first vs putting a queue in front of the sender? / What did you just implicitly decide about delivery guarantees that you didn't say out loud?
- **S3:** What breaks first on a morning fan-out to 50K members with the shape you just shipped?
- **S4:** Idempotency key vs at-most-once drop — which did the agent effectively choose, and what concrete failure does that create at this scale?

## Decomposition check (once, stage 2 or 3)

> If you only had time to build one more thing before this ships, what would you build and what would you explicitly defer?

Track whether they name a reason for the deferral or just list more features.

## Tracking (per stage)

- Clarifying Q before prompt?
- Prompt plain / drifted to framework?
- Predicted contents before reading?
- Restated agent output in own words?
- Tradeoff = mechanism + consequence vs buzzword?
- Complexity/perf named unprompted?
- Strongest / weakest verbatim quote

## Report

After stage 4 → `.drill/ROUND_A_FULL_REP_REPORT.md` using the template in `REPORT_TEMPLATE.md`.
