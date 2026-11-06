"""Refund status store."""

from __future__ import annotations

from refunds.models import RefundStatus


class RefundStore:
    """In-memory record of where each refund has got to."""

    def __init__(self) -> None:
        self._statuses: dict[str, RefundStatus] = {}

    def get(self, refund_id: str) -> RefundStatus | None:
        """The refund's recorded status, or None if we've never seen it."""
        return self._statuses.get(refund_id)

    def save(self, refund_id: str, status: RefundStatus) -> None:
        """Record a refund's status."""
        self._statuses[refund_id] = status