"""Queue worker for refund payouts (REF-09).

Pulls refund requests off the queue, pays the ones that are ready out
through PayRail, and records the outcome in the refund store.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from refunds.models import RefundStatus
from refunds.provider import PayoutProvider, ProviderTimeout
from refunds.queue import RefundQueue
from refunds.store import RefundStore

APPROVAL_THRESHOLD_PENCE = 50_000


@dataclass
class RunSummary:
    """What one pass over the queue did, by refund id."""

    paid: list[str] = field(default_factory=list)
    skipped_unapproved: list[str] = field(default_factory=list)
    timed_out: list[str] = field(default_factory=list)


class RefundNeedsApproval(RuntimeError):
    """A refund over the approval threshold has not had a second approval."""

    def __init__(self, refund_id: str) -> None:
        super().__init__(
            f"refund {refund_id} is over the approval threshold and unapproved"
        )
        self.refund_id = refund_id


def process_once(
    queue: RefundQueue, store: RefundStore, provider: PayoutProvider
) -> RunSummary:
    """Pay out one batch of refund requests from the queue."""
    summary = RunSummary()

    for refund in queue.receive():
        if store.get(refund.refund_id) is RefundStatus.PAID:
            queue.ack(refund.refund_id)  # already paid — stop it coming back
            continue

        if refund.amount_pence > APPROVAL_THRESHOLD_PENCE and not refund.approved:
            summary.skipped_unapproved.append(refund.refund_id)
            raise RefundNeedsApproval(refund.refund_id)

        try:
            provider.create_payout(
                refund.refund_id, refund.customer_id, refund.amount_pence
            )
        except ProviderTimeout:
            # PayRail didn't answer in time; leave the refund pending so the
            # next run can try it again.
            summary.timed_out.append(refund.refund_id)
            continue

        store.save(refund.refund_id, RefundStatus.PAID)
        queue.ack(refund.refund_id)
        summary.paid.append(refund.refund_id)

    return summary