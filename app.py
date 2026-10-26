"""OrderSprout: a local order book for small sellers."""

from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
import os
import secrets
import sqlite3

from flask import (
    Flask,
    abort,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)


STATUSES = ("New", "In progress", "Ready", "Delivered", "Cancelled")
PROJECT_FOLDER = Path(__file__).resolve().parent


def money_in_cents(text):
    """Convert an amount such as '10.25' into 1025 whole cents."""
    try:
        amount = Decimal(text.strip())
    except (InvalidOperation, AttributeError):
        raise ValueError("Enter a valid amount, such as 10.50.") from None

    if not amount.is_finite() or amount < 0 or amount > Decimal("999999.99"):
        raise ValueError("Enter an amount between 0 and 999,999.99.")

    cents = amount * 100

    if cents != cents.to_integral_value():
        raise ValueError("Use no more than two decimal places.")

    return int(cents)


def create_app(database_path=None):
    """Create and configure the Flask application."""
    app = Flask(__name__, root_path=str(PROJECT_FOLDER))

    app.config.update(
        SECRET_KEY=(
            os.environ.get("ORDERSPROUT_SECRET_KEY")
            or secrets.token_hex(32)
        ),
        DATABASE=str(
            database_path
            or PROJECT_FOLDER / "instance" / "orders.sqlite3"
        ),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        MAX_CONTENT_LENGTH=64 * 1024,
    )

    # Keep the database inside this project by default.
    Path(app.config["DATABASE"]).parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(app.config["DATABASE"]) as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer TEXT NOT NULL,
                item TEXT NOT NULL,
                delivery_date TEXT NOT NULL,
                total_cents INTEGER NOT NULL
                    CHECK(total_cents >= 0),
                paid_cents INTEGER NOT NULL
                    CHECK(paid_cents >= 0 AND paid_cents <= total_cents),
                status TEXT NOT NULL
                    CHECK(status IN (
                        'New',
                        'In progress',
                        'Ready',
                        'Delivered',
                        'Cancelled'
                    ))
            )
        """)

    def get_db():
        """Reuse one database connection during each request."""
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DATABASE"])
            g.db.row_factory = sqlite3.Row

        return g.db

    @app.teardown_appcontext
    def close_db(error=None):
        db = g.pop("db", None)

        if db is not None:
            db.close()

    @app.template_filter("money")
    def format_money(cents):
        return f"{cents // 100:,}.{cents % 100:02d}"

    @app.template_filter("friendly_date")
    def friendly_date(value):
        return date.fromisoformat(value).strftime("%d %b %Y")

    @app.context_processor
    def form_helpers():
        if "csrf_token" not in session:
            session["csrf_token"] = secrets.token_urlsafe(24)

        return {"csrf_token": session["csrf_token"]}

    @app.before_request
    def protect_forms():
        """Require a session token before accepting form submissions."""
        if request.method == "POST":
            expected = session.get("csrf_token", "")
            supplied = request.form.get("csrf_token", "")

            if not expected or not secrets.compare_digest(expected, supplied):
                abort(
                    400,
                    description=(
                        "Please refresh this page and submit the form again."
                    ),
                )

    @app.get("/")
    def index():
        rows = get_db().execute(
            "SELECT * FROM orders ORDER BY delivery_date, id DESC"
        ).fetchall()

        today = date.today().isoformat()

        active = [
            row
            for row in rows
            if row["status"] not in ("Delivered", "Cancelled")
        ]

        stats = {
            "active": len(active),
            "due_today": sum(
                row["delivery_date"] == today
                for row in active
            ),
            "outstanding": sum(
                row["total_cents"] - row["paid_cents"]
                for row in rows
                if row["status"] != "Cancelled"
            ),
        }

        return render_template(
            "index.html",
            orders=rows,
            stats=stats,
            today=today,
        )

    def order_form(order_id=None):
        existing = None

        if order_id is not None:
            existing = get_db().execute(
                "SELECT * FROM orders WHERE id = ?",
                (order_id,),
            ).fetchone()

            if existing is None:
                abort(404)

        if request.method == "POST":
            values = {
                key: request.form.get(key, "").strip()
                for key in (
                    "customer",
                    "item",
                    "delivery_date",
                    "total",
                    "paid",
                    "status",
                )
            }
        elif existing is not None:
            values = dict(existing)
            values["total"] = (
                f"{existing['total_cents'] // 100}."
                f"{existing['total_cents'] % 100:02d}"
            )
            values["paid"] = (
                f"{existing['paid_cents'] // 100}."
                f"{existing['paid_cents'] % 100:02d}"
            )
        else:
            values = {
                "customer": "",
                "item": "",
                "delivery_date": date.today().isoformat(),
                "total": "",
                "paid": "0.00",
                "status": "New",
            }

        errors = {}

        if request.method == "POST":
            for field, label in (
                ("customer", "Customer name"),
                ("item", "Order details"),
            ):
                if not values[field]:
                    errors[field] = f"{label} is required."
                elif len(values[field]) > 200:
                    errors[field] = (
                        f"Keep {label.lower()} within 200 characters."
                    )

            try:
                parsed_date = date.fromisoformat(values["delivery_date"])

                if parsed_date.isoformat() != values["delivery_date"]:
                    raise ValueError
            except ValueError:
                errors["delivery_date"] = "Choose a valid delivery date."

            for field in ("total", "paid"):
                try:
                    values[field + "_cents"] = money_in_cents(values[field])
                except ValueError as error:
                    errors[field] = str(error)

            if "total" not in errors and "paid" not in errors:
                if values["paid_cents"] > values["total_cents"]:
                    errors["paid"] = (
                        "Paid so far cannot be more than the order total."
                    )

            if values["status"] not in STATUSES:
                errors["status"] = "Choose a status from the list."

            if not errors:
                fields = (
                    values["customer"],
                    values["item"],
                    values["delivery_date"],
                    values["total_cents"],
                    values["paid_cents"],
                    values["status"],
                )

                if existing is None:
                    get_db().execute(
                        """
                        INSERT INTO orders (
                            customer,
                            item,
                            delivery_date,
                            total_cents,
                            paid_cents,
                            status
                        )
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        fields,
                    )
                else:
                    get_db().execute(
                        """
                        UPDATE orders
                        SET customer = ?,
                            item = ?,
                            delivery_date = ?,
                            total_cents = ?,
                            paid_cents = ?,
                            status = ?
                        WHERE id = ?
                        """,
                        fields + (order_id,),
                    )

                get_db().commit()
                return redirect(url_for("index"), code=303)

        return render_template(
            "order_form.html",
            values=values,
            errors=errors,
            statuses=STATUSES,
            editing=existing is not None,
        ), (422 if errors else 200)

    @app.route("/orders/new", methods=["GET", "POST"])
    def new_order():
        return order_form()

    @app.route("/orders/<int:order_id>/edit", methods=["GET", "POST"])
    def edit_order(order_id):
        return order_form(order_id)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=5001)