"""Refund request queue."""

from __future__ import annotations

from refunds.models import Refund


class RefundQueue:
    """In-memory refund queue with at-least-once delivery.

    A message is delivered again on every receive() until it is acked, the
    way a real queue redelivers a message after a visibility timeout.
    """

    def __init__(self, refunds: list[Refund] | None = None) -> None:
        self._pending: dict[str, Refund] = {
            refund.refund_id: refund for refund in refunds or []
        }

    def receive(self) -> list[Refund]:
        """Every refund awaiting processing, in delivery order."""
        return list(self._pending.values())

    def ack(self, refund_id: str) -> None:
        """Mark a refund as handled so it stops being delivered."""
        self._pending.pop(refund_id, None)