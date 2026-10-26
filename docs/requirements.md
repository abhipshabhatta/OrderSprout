# OrderSprout requirements

## Purpose

Help home bakers and handmade-product sellers track customer orders,
delivery dates, payments, and remaining balances.

## First version

The application runs locally for one seller.

### Orders

- Create an order with a customer name, order details, delivery date,
  total price, amount paid, and status.
- Display orders by delivery date, earliest first.
- Edit an existing order.
- Support these statuses: New, In progress, Ready, Delivered, Cancelled.
- Keep saved orders after restarting the application.

### Payments

- Record the cumulative amount paid manually.
- Use euros for the first version.
- Store money as whole cents.
- Calculate the remaining balance as total price minus amount paid.

### Dashboard

- Show the number of active orders.
- Show the number of active orders due today.
- Show outstanding payments, excluding cancelled orders.
- Treat delivered and cancelled orders as inactive.

### Validation

- Require a customer name and order details.
- Limit each of those fields to 200 characters.
- Require a valid delivery date.
- Accept monetary amounts from 0 to 999,999.99.
- Reject amounts with more than two decimal places.
- Reject payments greater than the order total.
- Reject statuses outside the supported list.

## Technology

- Python and Flask for application logic.
- HTML and CSS for pages.
- SQLite for persistent storage.
- pytest for automated tests.

## Outside the first version

- Seller accounts and sign-in.
- Online payment processing.
- Public hosting and deployment.
- Automated customer notifications.

## Completion checks

- A valid order can be created and edited.
- An order totaling EUR 40.00 with EUR 10.00 paid shows EUR 30.00 remaining.
- Invalid submissions show useful errors without saving changes.
- Orders remain available after restarting the application.
- Automated tests pass.
- Setup and usage instructions are documented.