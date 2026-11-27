# Test Plan: Checkout Feature (Sample Store, v2.4)

## 1. Objective
Verify that a customer can review a cart, enter shipping and payment details,
apply a discount code and place an order, and that totals, stock and
confirmation emails are correct.

## 2. Scope
**In scope:** cart review, shipping form, discount codes, payment (sandbox
gateway), order confirmation page and email, stock decrement.

**Out of scope:** product search, user registration, admin reporting, real
payment processing.

## 3. Test items and acceptance criteria
| ID | Requirement | Acceptance criterion |
|---|---|---|
| R1 | Cart totals | Subtotal = sum of line totals; tax and shipping are added correctly |
| R2 | Discount codes | Valid code reduces total once; expired or invalid code shows an error |
| R3 | Shipping form | Required fields enforced; postal code format validated |
| R4 | Payment | Approved card creates an order; declined card keeps the cart and shows a message |
| R5 | Confirmation | Order number shown and email sent within 2 minutes |
| R6 | Stock | Stock decrements on order; out-of-stock items cannot be purchased |

## 4. Approach
- **Functional:** manual test cases for every requirement (see `test-cases.csv`)
- **Boundary and negative testing:** empty fields, maximum lengths, quantity 0 and
  the maximum quantity, expired codes, repeated clicks on "Place order"
- **Regression:** automated suite for the core purchase path, run on each build
- **Smoke:** 10-minute checklist before every release
- **Compatibility:** latest Chrome, Firefox and Safari, plus one mobile viewport

## 5. Risks
| Risk | Impact | Mitigation |
|---|---|---|
| Double-submit creates duplicate orders | High | Dedicated negative test and idempotency check |
| Rounding differences in totals | High | Boundary cases with prices ending in .005 |
| Sandbox gateway outages | Medium | Retry window; record outage as blocked, not failed |
| Email delivery delays | Low | Check against a 2-minute threshold, with logs |

## 6. Entry criteria
Build deployed to the test environment, smoke checklist passes, test data loaded.

## 7. Exit criteria
- 100% of high-priority test cases executed and passing
- No open Critical or High defects
- At least 95% of all test cases passing, with Medium and Low defects triaged
- Regression suite green on the release candidate build

## 8. Deliverables
Test plan, test cases with results, defect log, a summary of quality metrics
(pass rate, defects by severity, open vs closed).
