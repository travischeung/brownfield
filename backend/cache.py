"""Process-local ticket cache.

Cache-aside / write-aside invalidation: populate on read; evict on successful
ticket mutations so the next GET reloads from the DB. Still process-local —
multi-worker deployments need a shared cache + the same invalidate-on-write.
"""

from typing import Any, Optional

_TICKET_CACHE: dict[int, Any] = {}


def get_cached_ticket(ticket_id: int) -> Optional[Any]:
    return _TICKET_CACHE.get(ticket_id)


def put_cached_ticket(ticket_id: int, ticket: Any) -> None:
    _TICKET_CACHE[ticket_id] = ticket


def invalidate_cached_ticket(ticket_id: int) -> None:
    """Write-aside: drop the entry after a successful DB write."""
    _TICKET_CACHE.pop(ticket_id, None)


def cache_stats() -> dict:
    return {"size": len(_TICKET_CACHE), "keys": list(_TICKET_CACHE.keys())}
