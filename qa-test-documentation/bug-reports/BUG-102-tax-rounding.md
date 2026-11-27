# BUG-102: Tax on 0.99 item is rounded down, total is one cent short

| Field | Value |
|---|---|
| Severity | **Major** |
| Priority | P2 |
| Status | Open |
| Build | 2.4.0-rc1 |
| Environment | Test, Firefox 132 on macOS |
| Related test case | TC-04 |

## Summary
For a 0.99 item with 8.5% tax, the checkout page shows tax of 0.08 and a total of
1.07 on the review page, but the order confirmation total is 1.06.

## Steps to reproduce
1. Add the item "Sticker" (price 0.99) to the cart.
2. Go to checkout with a shipping address in a state with 8.5% tax.
3. Note the tax and total on the review page.
4. Place the order and compare with the confirmation page.

## Expected result
Tax is 0.99 x 0.085 = 0.08415, which rounds to **0.08**. Total **1.07** on both pages.

## Actual result
Review page: tax 0.08, total 1.07.
Confirmation page and email: total **1.06**.

## Analysis
The two pages appear to round differently, with one rounding the tax and the
other truncating the total. The mismatch appears when the unrounded tax has a
fractional cent. It is most visible on low-priced items.

## Impact
The customer is shown one amount and charged another, which creates accounting
reconciliation problems.
