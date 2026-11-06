"""PayRail payout provider interface."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass
class PayoutReceipt:
    """PayRail's confirmation that a payout was created."""

    id: str
    refund_id: str
    customer_id: str
    amount_pence: int


class ProviderTimeout(Exception):
    """PayRail did not answer before the deadline.

    The outcome is ambiguous: PayRail may or may not have applied the payout.
    """


class PayoutProvider(Protocol):
    """Creates payouts with PayRail."""

    def create_payout(
        self,
        refund_id: str,
        customer_id: str,
        amount_pence: int,
        idempotency_key: str | None = None,
    ) -> PayoutReceipt: ...