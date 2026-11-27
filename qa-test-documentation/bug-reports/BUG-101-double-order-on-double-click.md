# BUG-101: Double-clicking "Place order" creates two orders and charges twice

| Field | Value |
|---|---|
| Severity | **Critical** |
| Priority | P1 (blocks release) |
| Status | Open |
| Build | 2.4.0-rc1 |
| Environment | Test, Chrome 130 on Windows 11, sandbox payment gateway |
| Related test case | TC-14 |

## Summary
Clicking **Place order** twice within about half a second submits the payment
form twice. Two orders are created and the sandbox gateway records two charges.

## Steps to reproduce
1. Add any in-stock item to the cart and go to checkout.
2. Enter valid shipping details and the sandbox card `4242 4242 4242 4242`.
3. On the review page, double-click **Place order** quickly.

## Expected result
One order is created and one charge is made. The button is disabled after the first click.

## Actual result
Two orders (`#10042` and `#10043`) are created with identical contents. The
gateway shows two charges. Two confirmation emails are sent.

## Reproducibility
5 out of 5 attempts. It does not reproduce when clicking slowly (more than 1 second apart).

## Notes
The button stays enabled until the response returns. A server-side idempotency
check on the cart or order token would also protect against retries and
network-level duplicates.

## Attachments
Screen recording `double-click.mp4`, network log showing two POST /checkout requests.
