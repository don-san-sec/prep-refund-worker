import pytest

from fakes import FakePayoutProvider
from refunds.provider import ProviderTimeout


def test_the_same_idempotency_key_returns_the_original_payout() -> None:
    provider = FakePayoutProvider()

    first = provider.create_payout("re_0001", "cus_0001", 2_500, idempotency_key="re_0001")
    second = provider.create_payout("re_0001", "cus_0001", 2_500, idempotency_key="re_0001")

    assert second is first
    assert len(provider.payouts) == 1


def test_without_an_idempotency_key_every_call_creates_a_payout() -> None:
    provider = FakePayoutProvider()

    provider.create_payout("re_0001", "cus_0001", 2_500)
    provider.create_payout("re_0001", "cus_0001", 2_500)

    assert len(provider.payouts) == 2


def test_different_idempotency_keys_create_different_payouts() -> None:
    provider = FakePayoutProvider()

    first = provider.create_payout("re_0001", "cus_0001", 2_500, idempotency_key="key-a")
    second = provider.create_payout("re_0001", "cus_0001", 2_500, idempotency_key="key-b")

    assert first is not second
    assert len(provider.payouts) == 2


def test_a_refund_configured_to_time_out_raises() -> None:
    provider = FakePayoutProvider(timeout_refund_ids={"re_0001"})

    with pytest.raises(ProviderTimeout):
        provider.create_payout("re_0001", "cus_0001", 2_500, idempotency_key="re_0001")
