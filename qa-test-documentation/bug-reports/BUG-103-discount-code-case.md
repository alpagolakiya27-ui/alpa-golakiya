# BUG-103: Discount codes are case-sensitive

| Field | Value |
|---|---|
| Severity | **Minor** |
| Priority | P3 |
| Status | Open |
| Build | 2.4.0-rc1 |
| Environment | Test, Chrome 130 on Windows 11 |
| Related test case | TC-08 |

## Summary
`SAVE10` is accepted, but `save10` shows "Invalid code".

## Steps to reproduce
1. Add an item to the cart and open checkout.
2. Enter `save10` in the discount field and click **Apply**.

## Expected result
Codes are case-insensitive (per requirement R2). The 10% discount is applied.

## Actual result
Error message "Invalid discount code". Entering `SAVE10` works.

## Notes
Low severity because a workaround exists, but it likely causes support tickets
from mobile users whose keyboards auto-lowercase.
