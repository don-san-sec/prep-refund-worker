# Refund payouts

Customers leaving Brightwatt Energy with credit on their account get that
credit refunded to their bank via PayRail payouts. Refund requests arrive on a
queue and a worker pays them out.

## Context

Brightwatt Energy is an app-first UK domestic energy supplier. About 180,000
customers pay a monthly bill, and every amount is stored in whole pence. When a
customer leaves with credit left on their account, that credit is paid back to
their bank through PayRail, our payout provider.

Refund requests arrive on a queue. The ticket for this work is REF-09:

> "Process refund requests from the queue automatically."

## The payouts runbook's rules

These come from the payments team's payouts runbook. The refunds service must
follow them exactly — a customer paid twice, or not at all, is a reportable
payments incident.

1. The queue delivers messages **at least once**: the same message can be
   redelivered — for example after a visibility timeout — and the refunds
   service runs **two worker processes concurrently**.
2. Each refund must be paid out **exactly once** — across redeliveries,
   concurrent workers, and process crashes.
3. PayRail honours **idempotency keys** on payouts for 24 hours: a repeated
   request with the same key returns the original payout without creating
   another.
4. Refunds over **50,000p (strictly greater)** require a second approval
   before payout. Unapproved refunds are **left in the queue** (skipped this
   run): they must not be paid, and they must not block other refunds.
5. A payout **timeout is ambiguous** — PayRail may or may not have applied it.
   A timed-out refund must be marked for **manual reconciliation** and never
   automatically re-paid.
6. Every payout attempt is **recorded for audit**, with the provider payout id
   when known.

## How it works

```
src/refunds/
  models.py           Refund and its status
  provider.py         PayoutProvider: PayRail payouts
  queue.py            RefundQueue: at-least-once delivery
  store.py            RefundStore: refund status
tests/
```

The queue, the store and the PayRail interface are in place and tested. The
worker itself is not implemented yet — that is ticket REF-09.

## Running locally

```
uv sync
uv run pytest -q
```

## Your task

A colleague has opened a PR: https://github.com/don-san-sec/prep-refund-worker/pull/1. You are the owner of this feature. Review the PR and decide whether to accept or reject it, and explain why.
