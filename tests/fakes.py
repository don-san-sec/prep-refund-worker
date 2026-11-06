"""Test doubles for the refund service."""

from __future__ import annotations

from refunds.provider import PayoutReceipt, ProviderTimeout


class FakePayoutProvider:
    """In-memory PayRail stand-in.

    Honours idempotency keys the way PayRail does: a repeated request with
    the same key returns the original payout without creating another.
    Refund ids in `timeout_refund_ids` raise ProviderTimeout, standing in
    for a payout request that never came back.
    """

    def __init__(self, timeout_refund_ids: set[str] | None = None) -> None:
        self.payouts: list[PayoutReceipt] = []
        self._by_key: dict[str, PayoutReceipt] = {}
        self._timeout_refund_ids = timeout_refund_ids or set()
        self._next_id = 1

    def create_payout(
        self,
        refund_id: str,
        customer_id: str,
        amount_pence: int,
        idempotency_key: str | None = None,
    ) -> PayoutReceipt:
        if refund_id in self._timeout_refund_ids:
            raise ProviderTimeout(f"PayRail did not answer for refund {refund_id}")

        if idempotency_key is not None and idempotency_key in self._by_key:
            return self._by_key[idempotency_key]

        receipt = PayoutReceipt(
            id=f"po_{self._next_id:06d}",
            refund_id=refund_id,
            customer_id=customer_id,
            amount_pence=amount_pence,
        )
        self._next_id += 1
        self.payouts.append(receipt)
        if idempotency_key is not None:
            self._by_key[idempotency_key] = receipt
        return receipt