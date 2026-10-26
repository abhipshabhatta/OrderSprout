"""Tests for order creation, editing, validation, and persistence."""

from datetime import date
import sqlite3

import pytest

from app import create_app


@pytest.fixture
def app(tmp_path):
    """Give each test its own temporary database."""
    application = create_app(tmp_path / "test-orders.sqlite3")
    application.config.update(
        TESTING=True,
        SECRET_KEY="ordersprout-test-secret",
    )
    return application


@pytest.fixture
def client(app):
    return app.test_client()


def valid_order(**changes):
    """Build valid form data, allowing individual fields to change."""
    data = {
        "customer": "Maya",
        "item": "One birthday cake",
        "delivery_date": date.today().isoformat(),
        "total": "40.00",
        "paid": "10.00",
        "status": "New",
    }
    data.update(changes)
    return data


def submit_order(client, data, path="/orders/new"):
    """Get a real form token before submitting through the test client."""
    response = client.get(path)
    assert response.status_code == 200

    with client.session_transaction() as session:
        token = session["csrf_token"]

    return client.post(path, data={**data, "csrf_token": token})


def saved_orders(app):
    """Read stored orders independently of the page output."""
    with sqlite3.connect(app.config["DATABASE"]) as database:
        database.row_factory = sqlite3.Row
        return database.execute(
            "SELECT * FROM orders ORDER BY id"
        ).fetchall()


def test_empty_dashboard(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "Your first order starts here." in response.get_data(as_text=True)


def test_create_order(client, app):
    response = submit_order(client, valid_order())

    assert response.status_code == 303

    orders = saved_orders(app)
    assert len(orders) == 1
    assert orders[0]["customer"] == "Maya"
    assert orders[0]["total_cents"] == 4000
    assert orders[0]["paid_cents"] == 1000
    assert orders[0]["status"] == "New"

    page = client.get("/").get_data(as_text=True)
    assert "Maya" in page
    assert "€30.00" in page


def test_edit_payment_and_status(client, app):
    submit_order(client, valid_order())
    order_id = saved_orders(app)[0]["id"]

    response = submit_order(
        client,
        valid_order(paid="40.00", status="Ready"),
        path=f"/orders/{order_id}/edit",
    )

    assert response.status_code == 303

    orders = saved_orders(app)
    assert len(orders) == 1
    assert orders[0]["paid_cents"] == 4000
    assert orders[0]["status"] == "Ready"

    page = client.get("/").get_data(as_text=True)
    assert "€0.00" in page


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"customer": ""}, "Customer name is required."),
        ({"item": ""}, "Order details is required."),
        ({"customer": "M" * 201}, "within 200 characters"),
        ({"delivery_date": "2026-02-30"}, "Choose a valid delivery date."),
        ({"total": "abc"}, "Enter a valid amount"),
        ({"total": "-1"}, "Enter an amount between"),
        ({"total": "1000000"}, "Enter an amount between"),
        ({"total": "10.001"}, "Use no more than two decimal places."),
        ({"total": "NaN"}, "Enter an amount between"),
        ({"paid": "41.00"}, "Paid so far cannot be more"),
        ({"status": "Unknown"}, "Choose a status from the list."),
    ],
)
def test_invalid_order_is_not_saved(client, app, changes, message):
    response = submit_order(client, valid_order(**changes))

    assert response.status_code == 422
    assert message in response.get_data(as_text=True)
    assert saved_orders(app) == []


def test_invalid_edit_preserves_existing_order(client, app):
    submit_order(client, valid_order())
    original = dict(saved_orders(app)[0])

    response = submit_order(
        client,
        valid_order(paid="50.00"),
        path=f"/orders/{original['id']}/edit",
    )

    assert response.status_code == 422
    assert dict(saved_orders(app)[0]) == original


def test_submission_without_csrf_token_is_rejected(client, app):
    response = client.post("/orders/new", data=valid_order())

    assert response.status_code == 400
    assert saved_orders(app) == []


def test_submission_with_wrong_csrf_token_is_rejected(client, app):
    client.get("/orders/new")

    response = client.post(
        "/orders/new",
        data={**valid_order(), "csrf_token": "incorrect-token"},
    )

    assert response.status_code == 400
    assert saved_orders(app) == []


def test_missing_order_returns_404(client):
    response = client.get("/orders/999/edit")

    assert response.status_code == 404


def test_orders_survive_application_restart(client, app):
    submit_order(client, valid_order())

    restarted_app = create_app(app.config["DATABASE"])
    restarted_app.config.update(
        TESTING=True,
        SECRET_KEY="ordersprout-test-secret",
    )

    with restarted_app.test_client() as restarted_client:
        response = restarted_client.get("/")

    assert response.status_code == 200
    assert "Maya" in response.get_data(as_text=True)

    orders = saved_orders(restarted_app)
    assert len(orders) == 1
    assert orders[0]["total_cents"] == 4000
    assert orders[0]["paid_cents"] == 1000