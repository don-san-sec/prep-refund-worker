from refunds.models import Refund
from refunds.queue import RefundQueue


def test_unacked_refunds_are_redelivered() -> None:
    queue = RefundQueue([Refund("re_0001", "cus_0001", 2_500)])

    first = queue.receive()
    second = queue.receive()

    assert [r.refund_id for r in first] == ["re_0001"]
    assert [r.refund_id for r in second] == ["re_0001"]  # at least once


def test_acked_refunds_are_not_redelivered() -> None:
    queue = RefundQueue([Refund("re_0001", "cus_0001", 2_500)])
    queue.receive()
    queue.ack("re_0001")

    assert queue.receive() == []


def test_receive_returns_only_the_refunds_still_pending() -> None:
    queue = RefundQueue(
        [
            Refund("re_0001", "cus_0001", 2_500),
            Refund("re_0002", "cus_0002", 1_000),
        ]
    )
    queue.receive()
    queue.ack("re_0001")

    assert [r.refund_id for r in queue.receive()] == ["re_0002"]
