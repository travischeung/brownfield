"""Process-local ticket cache.

Populated on read. There is no invalidation hook on write paths —
callers that mutate tickets leave stale entries until process restart.
"""

from typing import Any, Optional

_TICKET_CACHE: dict[int, Any] = {}


def get_cached_ticket(ticket_id: int) -> Optional[Any]:
    return _TICKET_CACHE.get(ticket_id)


def put_cached_ticket(ticket_id: int, ticket: Any) -> None:
    _TICKET_CACHE[ticket_id] = ticket


def cache_stats() -> dict:
    return {"size": len(_TICKET_CACHE), "keys": list(_TICKET_CACHE.keys())}
