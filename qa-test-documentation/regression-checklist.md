# Release Regression Checklist: Checkout

Run on the release candidate build. Record build number, tester, date and result.

**Build:** ________  **Tester:** ________  **Date:** ________

## Smoke (about 10 minutes, stop and escalate if any fail)
- [ ] Site loads and a product page opens
- [ ] Add to cart works and the cart count updates
- [ ] Checkout page opens for a guest user
- [ ] Sandbox card order completes and shows an order number
- [ ] Confirmation email arrives

## Core regression
### Cart and totals
- [ ] Subtotal, tax and shipping calculate correctly (TC-01, TC-04)
- [ ] Quantity limits enforced (TC-02, TC-03)

### Discounts
- [ ] Valid code applies; expired and repeated codes are rejected (TC-05 to TC-08)

### Shipping and payment
- [ ] Required-field validation works (TC-09, TC-10)
- [ ] Approved and declined cards behave correctly (TC-12, TC-13)
- [ ] Double-click on Place order creates one order (TC-14)

### Stock
- [ ] Stock decrements and out-of-stock items are blocked (TC-18 to TC-20)

## Compatibility spot check
- [ ] Chrome  - [ ] Firefox  - [ ] Safari  - [ ] Mobile viewport (375 px wide)

## Sign-off
- [ ] No open Critical or High defects
- [ ] Results and defect log shared with the team

**Decision:** Go / No-go  **Notes:** ________
