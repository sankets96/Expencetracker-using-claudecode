from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import init_db, seed_db, create_user, get_user_by_email, get_expenses_by_user, create_expense, get_expense_by_id, update_expense, delete_expense

app = Flask(__name__)
app.secret_key = "dev-secret-key"

with app.app_context():
    init_db()
    seed_db()


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        if not full_name or not email or not password:
            return render_template("register.html", error="All fields are required.")

        hashed_password = generate_password_hash(password)
        if create_user(full_name, email, hashed_password):
            flash("Account created successfully! Please sign in.")
            return redirect(url_for("login"))
        else:
            return render_template("register.html", error="Email already exists.")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            return render_template("login.html", error="All fields are required.")

        user = get_user_by_email(email)

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            flash("Welcome back!")
            return redirect(url_for("profile"))
        else:
            return render_template("login.html", error="Invalid email or password.")

    return render_template("login.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("login"))


@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect(url_for("login"))

    # Hardcoded data for UI validation as per spec 04-profile-page
    user_info = {
        "name": "Sanket Suryavanshi",
        "email": "sanket@example.com",
        "member_since": "January 2024",
        "initials": "SS"
    }

    summary_stats = {
        "total_spent": 1250.75,
        "transaction_count": 42,
        "top_category": "Food"
    }

    recent_expenses = [
        {"id": 1, "date": "2024-03-20", "description": "Lunch at Cafe", "category": "Food", "amount": 15.50},
        {"id": 2, "date": "2024-03-19", "description": "Gas refill", "category": "Transport", "amount": 30.00},
        {"id": 3, "date": "2024-03-18", "description": "Monthly Internet", "category": "Bills", "amount": 120.00},
        {"id": 4, "date": "2024-03-17", "description": "Pharmacy", "category": "Health", "amount": 45.00},
    ]

    category_breakdown = [
        {"category": "Food", "amount": 450.00, "percentage": 36},
        {"category": "Transport", "amount": 200.00, "percentage": 16},
        {"category": "Bills", "amount": 300.00, "percentage": 24},
        {"category": "Health", "amount": 150.00, "percentage": 12},
        {"category": "Other", "amount": 150.75, "percentage": 12},
    ]

    return render_template(
        "profile.html",
        user=user_info,
        stats=summary_stats,
        expenses=recent_expenses,
        breakdown=category_breakdown
    )


@app.route("/expenses/add", methods=["GET", "POST"])
def add_expense():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        amount = request.form.get("amount")
        category = request.form.get("category")
        date = request.form.get("date")
        description = request.form.get("description")

        if not amount or not category or not date:
            return render_template("add_expense.html", error="Amount, category, and date are required.")

        try:
            create_expense(session["user_id"], float(amount), category, date, description)
            flash("Expense added successfully!")
            return redirect(url_for("profile"))
        except Exception as e:
            return render_template("add_expense.html", error=f"An error occurred: {e}")

    return render_template("add_expense.html")


@app.route("/expenses/<int:id>/edit", methods=["GET", "POST"])
def edit_expense(id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    expense = get_expense_by_id(id, session["user_id"])

    if not expense:
        return "Expense not found or access denied.", 404

    if request.method == "POST":
        amount = request.form.get("amount")
        category = request.form.get("category")
        date = request.form.get("date")
        description = request.form.get("description")

        if not amount or not category or not date:
            return render_template("edit_expense.html", expense=expense, error="Amount, category, and date are required.")

        try:
            update_expense(id, session["user_id"], float(amount), category, date, description)
            flash("Expense updated successfully!")
            return redirect(url_for("profile"))
        except Exception as e:
            return render_template("edit_expense.html", expense=expense, error=f"An error occurred: {e}")

    return render_template("edit_expense.html", expense=expense)


@app.route("/expenses/<int:id>/delete", methods=["POST"])
def delete_expense(id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    expense = get_expense_by_id(id, session["user_id"])

    if not expense:
        return "Expense not found or access denied.", 404

    delete_expense(id, session["user_id"])
    flash("Expense deleted successfully!")
    return redirect(url_for("profile"))


if __name__ == "__main__":
    app.run(debug=True, port=5001)
