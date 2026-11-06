import pytest

from fakes import FakePayoutProvider
from refunds.models import Refund, RefundStatus
from refunds.queue import RefundQueue
from refunds.store import RefundStore
from refunds.worker import APPROVAL_THRESHOLD_PENCE, RefundNeedsApproval, process_once


def test_a_refund_is_paid_once_and_marked_paid() -> None:
    refund = Refund("re_0001", "cus_0001", 2_500)
    queue = RefundQueue([refund])
    store = RefundStore()
    provider = FakePayoutProvider()

    summary = process_once(queue, store, provider)

    assert summary.paid == ["re_0001"]
    assert store.get("re_0001") is RefundStatus.PAID
    assert len(provider.payouts) == 1
    assert provider.payouts[0].amount_pence == 2_500
    assert queue.receive() == []  # acked, so it won't come back


def test_a_refund_at_the_threshold_is_paid_without_approval() -> None:
    refund = Refund("re_0002", "cus_0002", APPROVAL_THRESHOLD_PENCE)
    queue = RefundQueue([refund])
    store = RefundStore()
    provider = FakePayoutProvider()

    summary = process_once(queue, store, provider)

    assert summary.paid == ["re_0002"]
    assert store.get("re_0002") is RefundStatus.PAID


def test_a_refund_over_the_threshold_needs_approval_before_payout() -> None:
    refund = Refund("re_0003", "cus_0003", APPROVAL_THRESHOLD_PENCE + 1)
    queue = RefundQueue([refund])
    store = RefundStore()
    provider = FakePayoutProvider()

    with pytest.raises(RefundNeedsApproval):
        process_once(queue, store, provider)

    assert provider.payouts == []
    assert store.get("re_0003") is None


def test_a_refund_already_marked_paid_is_not_paid_again() -> None:
    refund = Refund("re_0004", "cus_0004", 2_500)
    queue = RefundQueue([refund])
    store = RefundStore()
    store.save("re_0004", RefundStatus.PAID)
    provider = FakePayoutProvider()

    summary = process_once(queue, store, provider)

    assert summary.paid == []
    assert provider.payouts == []
