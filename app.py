# app.py
from flask import Flask, render_template
from flask import request, redirect
import database

app = Flask(__name__)

from flask import render_template

@app.errorhandler(403)
def forbidden(e):
    return render_template("403.html"), 403

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500



# ---------------- AUTH ----------------

from flask import Flask, render_template, request, redirect, session, abort

app = Flask(__name__)
app.secret_key = "super-secret-key"

# ساین آپ
@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        first = request.form["first_name"]
        last = request.form["last_name"]
        email = request.form["email"]
        password = request.form["password"]
        phone = request.form["phone_number"]
        role = request.form.get("role", "user")  # اختیاری، default user

        database.create_user(first, last, email, password, phone, role)
        return redirect("/login")

    return render_template("signup.html")

# لاگین
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = database.verify_user(email, password)
        if user:
            session["user_id"] = user["user_id"]
            session["role"] = user["role"]

            # redirect بر اساس role
            return redirect("/dashboard")
        return "Invalid credentials", 403

    return render_template("login.html")

# خروج
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")



from functools import wraps
from flask import abort

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated

from functools import wraps
from flask import session, redirect, render_template

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/login")

        if session.get("role") != "admin":
            return render_template("403.html"), 403

        return f(*args, **kwargs)
    return decorated



# ---------------- CARS ----------------

@app.route("/cars")
@login_required
def cars_list():
    cars = database.get_all_cars()
    return render_template("cars_list.html", cars=cars)
  
@app.route("/cars/add", methods=["GET", "POST"])
@admin_required
def add_car():
        
    if request.method == "POST":
        database.add_car(
            request.form["name"],
            request.form["brand"],
            request.form["body_type"],
            int(request.form["year"]),
            float(request.form["price"]),
            request.form["description"]
        )
        return redirect("/cars")

    return render_template("add_car.html")

from datetime import datetime

from datetime import date

@app.route("/rent/<int:car_id>", methods=["GET","POST"])
@login_required
def rent_car(car_id):
    car = database.get_car_by_id(car_id)
    if not car:
        return "Car not found", 404
    if car["status"] != "available":
        return "Car not available", 400

    if request.method == "POST":
        start_date = request.form["start_date"]
        end_date = request.form["end_date"]
        pickup_location = request.form["pickup_location"].strip()

        if not pickup_location:
            return "Pickup location required", 400

        days = (datetime.fromisoformat(end_date) - datetime.fromisoformat(start_date)).days
        if days <= 0:
            return "Invalid date range", 400

        total_price = days * float(car["daily_rent_price"])
        user_id = session["user_id"]

        database.add_rental(user_id, car_id, start_date, end_date, pickup_location, total_price)
        return redirect("/my-rentals")

    return render_template("rent_car.html", car=car)

@app.route("/cars/search")
@login_required
def search_cars():
    brand = request.args.get("brand", "").strip()
    status = request.args.get("status", "").strip()

    cars = database.search_cars(brand, status)
    return render_template("cars_list.html", cars=cars)
  
@app.route("/dashboard/search/cars")
@login_required
def dashboard_search_cars():
    brand = request.args.get("brand", "").strip()
    status = request.args.get("status", "").strip()

    cars = database.search_cars(brand, status)

    return render_template(
        "cars_list.html",
        cars=cars,
        from_dashboard=True
    )
    
# ---------------- USERS ----------------

  
@app.route("/payments/pay/<int:rental_id>", methods=["GET","POST"])
@login_required
def pay_rental(rental_id):
    user_id = session["user_id"]
    rental = database.get_rental_by_id(rental_id)

    if not rental or rental["user_id"] != user_id:
        return "Unauthorized", 403
    if rental["status"] != "completed":
        return "Rental not completed yet", 400

    paid = database.get_total_paid_for_rental(rental_id)
    remaining = float(rental["total_price"]) - float(paid)

    if remaining <= 0:
        return "Already paid", 400

    if request.method == "POST":
        amount = float(request.form["amount"])
        method = request.form["payment_method"]
        if amount <= 0 or amount > remaining:
            return "Invalid amount", 400

        database.add_payment(rental_id, amount, method)

        # اگر تسویه کامل شد
        total_paid = paid + amount
        if total_paid >= float(rental["total_price"]):
            database.mark_payments_completed(rental_id)

        return redirect("/my-rentals")

    return render_template("pay_rental.html", rental=rental, remaining=remaining)



# ---------------- RENTALS ----------------

@app.route("/rentals")
@admin_required
def rentals_list():
    rentals = database.get_all_rentals()
    return render_template("rentals_list.html", rentals=rentals)

@app.route("/rentals/complete/<int:rental_id>")
@admin_required
def complete_rental_admin(rental_id):
    database.complete_rental(rental_id)
    return redirect("/rentals")
  
@app.route("/rentals/complete/<int:rental_id>")
@login_required
def complete_rental_user(rental_id):
    database.complete_rental(rental_id)
    return redirect("/rentals")

@app.route("/my-rentals")
@login_required
def my_rentals():
    user_id = session["user_id"]

    rentals = database.get_user_rentals(user_id)

    return render_template(
        "my_rentals.html",
        rentals=rentals,
        from_dashboard=True
    )


  
# ---------------- PAYMENTS ----------------

@app.route("/payments/add/<int:rental_id>", methods=["GET", "POST"])
@login_required
def add_payment(rental_id):
    rental = database.get_rental_by_id(rental_id)

    if not rental:
        return "Rental not found", 404

    if request.method == "POST":
        amount = float(request.form["amount"])
        method = request.form["payment_method"]

        if amount <= 0:
            return "Invalid amount", 400

        database.add_payment(
            rental_id=rental_id,
            amount=amount,
            payment_method=method
        )

        return redirect("/rentals")

    return render_template(
        "add_payment.html",
        rental=rental
    )
    
@app.route("/payments")
@admin_required
def payments_list():
    payments = database.get_all_payments()
    return render_template("payments_list.html", payments=payments)

  
@app.route("/payments/<int:rental_id>")
@admin_required
def payments_for_rental(rental_id):
    payments = database.get_payments_by_rental(rental_id)
    return render_template("payments_list.html", payments=payments)

  
# ---------------- Dashboard ----------------
 
@app.route("/dashboard")
@login_required
def dashboard():
    if session.get("role") == "admin":
        stats = database.get_admin_dashboard_stats()
        return render_template("admin_dashboard.html", stats=stats)
    else:
        stats = database.get_user_dashboard_stats(session["user_id"])
        return render_template("user_dashboard.html", stats=stats)

  
# ---------------- MAIN ----------------

if __name__ == "__main__":
    app.run(debug=False)
