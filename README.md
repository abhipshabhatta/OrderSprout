# OrderSprout

A local order book for home bakers and handmade-product sellers,
adapted from the small-order-book starter.

Built with Python, Flask, HTML, CSS, and SQLite.

## Project status

The first local application milestone and continuous integration are
merged into main.

Creating orders, editing payments and statuses, and retaining data
after restarting have been checked manually.

All 19 automated tests pass locally and in GitHub Actions.
Further improvements will be developed in separate milestones.

## Features

- Add customer orders and delivery dates.
- List orders by delivery date, earliest first.
- Record total price and cumulative payments received.
- Update order details and status.
- Calculate the remaining balance.
- View active orders, orders due today, and outstanding payments.
- Save orders locally in SQLite.

Supported statuses: New, In progress, Ready, Delivered, Cancelled.

Amounts use euros and are stored as whole cents.

## Local setup

Install Python 3.9 or newer and Git.

Clone the repository and enter its folder:

```bash
git clone https://github.com/abhipshabhatta/OrderSprout.git
cd OrderSprout
```

Create a virtual environment for a fresh clone:

```bash
python3 -m venv .venv
```

Activate it and install dependencies:

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Start the application:

```bash
python -m flask --app 'app:create_app()' run --host 127.0.0.1 --port 5002
```

Open http://127.0.0.1:5002 in your browser.

Keep Terminal running while using the application.
Press Control + C to stop it.

## Saved orders

Orders are stored locally in instance/orders.sqlite3.
The application creates this database automatically.
The database is excluded from Git.

## Manual checks completed

- Created an order with a total of EUR 40.00 and EUR 10.00 paid.
- Confirmed the remaining balance was EUR 30.00.
- Updated the payment to EUR 40.00 and the status to Ready.
- Confirmed the remaining balance became EUR 0.00.
- Restarted the application and confirmed the order remained saved.

## Automated tests

Install the development dependencies with your virtual environment active:

```bash
python -m pip install -r requirements-dev.txt
```

Run the tests from the project folder:

```bash
python -m pytest -q
```

The initial suite contains 19 tests covering:

- The empty dashboard.
- Creating orders and displaying the remaining balance.
- Editing payments and order status.
- Rejecting invalid inputs without saving them.
- Preserving existing data when an edit fails validation.
- Rejecting missing or incorrect form security tokens.
- Returning 404 for an order that does not exist.
- Retaining orders across application restarts.

Tests use temporary SQLite databases, separate from your local orders.

Latest local result: 19 passed.

## Continuous integration

GitHub Actions runs the automated test suite on every push and on
pull requests targeting main.

The workflow uses Ubuntu and Python 3.13, installs development
dependencies, and runs python -m pytest -q.

Workflow configuration: .github/workflows/tests.yml

To view results, open the repository's Actions tab and select Tests.
A failed run should be investigated before merging.

## Development approach

Work is organized into branches, meaningful commits, and pull requests.
Completed changes are merged into main after review and passing checks.

- Project foundation: merged through pull request #1.
- Local order management application: merged through pull request #2.
- Continuous integration: merged through pull request #3.

## Documentation

- [Requirements](docs/requirements.md)
- [Development log](docs/development-log.md)
