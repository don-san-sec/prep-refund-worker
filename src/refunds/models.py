"""Refund models."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class RefundStatus(StrEnum):
    """Where a refund has got to."""

    PENDING = "pending"
    PAID = "paid"
    NEEDS_RECONCILIATION = "needs_reconciliation"


@dataclass
class Refund:
    """A request to pay a leaving customer's credit back to their bank.

    Amounts are whole pence. `approved` records the second approval the
    runbook requires for refunds over 50,000p.
    """

    refund_id: str
    customer_id: str
    amount_pence: int
    approved: bool = False
    status: RefundStatus = RefundStatus.PENDING