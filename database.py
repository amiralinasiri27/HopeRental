# database.py
import psycopg2
from psycopg2.extras import RealDictCursor

def get_connection():
    return psycopg2.connect(
        dbname="hoperental",
        user="postgres",
        password="1234",
        host="localhost",
        port="5432"
    )

# ---------------- CARS ----------------

def get_all_cars():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT car_id, name, brand, body_type, production_year, daily_rent_price, status, description
        FROM cars
        ORDER BY car_id DESC
    """)
    cars = cur.fetchall()
    cur.close()
    conn.close()
    return cars

def add_car(name, brand, body_type, year, price, description):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO cars
        (name, brand, body_type, production_year, daily_rent_price, description)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (name, brand, body_type, year, price, description))
    conn.commit()
    cur.close()
    conn.close()

def get_car_by_id(car_id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM cars WHERE car_id = %s", (car_id,))
    car = cur.fetchone()
    cur.close()
    conn.close()
    return car

# بروزرسانی خودرو
def update_car(car_id, name, brand, daily_price, status):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE cars
        SET name = %s,
            brand = %s,
            daily_price = %s,
            status = %s
        WHERE car_id = %s
    """, (name, brand, daily_price, status, car_id))
    conn.commit()
    cur.close()
    conn.close()


def get_active_rentals_for_car(car_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT 1 FROM rentals
        WHERE car_id = %s AND status = 'active'
    """, (car_id,))
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result


def delete_car(car_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM cars WHERE car_id = %s", (car_id,))
    conn.commit()
    cur.close()
    conn.close()


def search_cars(brand, status):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    query = """
        SELECT
            car_id,
            name,
            brand,
            body_type,
            production_year,
            daily_rent_price,
            status
        FROM cars
        WHERE 1=1
    """
    params = []

    if brand:
        query += " AND brand ILIKE %s"
        params.append(f"%{brand}%")

    if status:
        query += " AND status = %s"
        params.append(status)

    cur.execute(query, params)
    cars = cur.fetchall()
    conn.close()
    return cars

def set_car_available(car_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE cars
        SET status = 'available'
        WHERE car_id = %s
    """, (car_id,))
    conn.commit()
    cur.close()


# ---------------- RENTALSS ----------------

def add_rental(
    user_id,
    car_id,
    start_date,
    end_date,
    pickup_location,
    total_price
):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO rentals
        (
            user_id,
            car_id,
            start_date,
            end_date,
            pickup_location,
            total_price,
            status
        )
        VALUES (%s, %s, %s, %s, %s, %s, 'active')
    """, (
        user_id,
        car_id,
        start_date,
        end_date,
        pickup_location,
        total_price
    ))

    cur.execute("""
        UPDATE cars
        SET status = 'rented'
        WHERE car_id = %s
    """, (car_id,))

    conn.commit()
    cur.close()
    conn.close()

def get_all_rentals():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT
            r.rental_id,
            r.start_date,
            r.end_date,
            r.total_price,
            r.status AS rental_status,

            u.first_name,
            u.last_name,

            c.name AS car_name,
            c.brand
        FROM rentals r
        JOIN users u ON r.user_id = u.user_id
        JOIN cars c ON r.car_id = c.car_id
        ORDER BY r.rental_id DESC
    """)

    rentals = cur.fetchall()
    cur.close()
    conn.close()
    return rentals
  
def get_rental_by_id(rental_id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT * FROM rentals WHERE rental_id = %s
    """, (rental_id,))
    rental = cur.fetchone()
    cur.close()
    conn.close()
    return rental

def get_rentals_by_user(user_id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT
            r.rental_id,
            r.start_date,
            r.end_date,
            r.total_price,
            r.status,

            c.name AS car_name,
            c.brand
        FROM rentals r
        JOIN cars c ON r.car_id = c.car_id
        WHERE r.user_id = %s
        ORDER BY r.created_at DESC
    """, (user_id,))

    rentals = cur.fetchall()
    cur.close()
    conn.close()
    return rentals
  
def complete_rental(rental_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE rentals
        SET status = 'completed'
        WHERE rental_id = %s
    """, (rental_id,))

    cur.execute("""
        UPDATE cars
        SET status = 'available'
        WHERE car_id = (
            SELECT car_id FROM rentals WHERE rental_id = %s
        )
    """, (rental_id,))

    conn.commit()
    cur.close()
    conn.close()

def update_rental_status(rental_id, new_status):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE rentals
        SET status = %s
        WHERE rental_id = %s
    """, (new_status, rental_id))
    conn.commit()
    cur.close()
    conn.close()


# ---------------- PAYMENTS ----------------

def add_payment(rental_id, amount, method):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO payments (rental_id, amount, payment_date, status, payment_method)
        VALUES (%s, %s, NOW(), 'completed', %s)
    """, (rental_id, amount, method))
    conn.commit()
    cur.close()
    conn.close()


    
def get_all_payments():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT
            p.payment_id,
            p.amount,
            p.payment_method,
            p.status AS payment_status,
            p.payment_date,

            r.rental_id,
            r.total_price,
            r.start_date,
            r.end_date,

            u.first_name || ' ' || u.last_name AS user_name
        FROM payments p
        JOIN rentals r ON p.rental_id = r.rental_id
        JOIN users u ON r.user_id = u.user_id
        ORDER BY p.payment_date DESC
    """)

    payments = cur.fetchall()
    cur.close()
    conn.close()
    return payments


def get_total_paid_for_rental(rental_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM payments
        WHERE rental_id = %s
    """, (rental_id,))
    total = cur.fetchone()[0]
    cur.close()
    conn.close()
    return float(total)

def mark_payments_completed(rental_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE payments
        SET status = 'completed'
        WHERE rental_id = %s
    """, (rental_id,))
    conn.commit()
    cur.close()
    conn.close()
    
def get_payments_by_rental(rental_id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT
            p.payment_id,
            p.amount,
            p.payment_date,
            p.status AS payment_status,
            p.payment_method,
            r.rental_id,
            r.start_date,
            r.end_date,
            u.first_name || ' ' || u.last_name AS user_name
        FROM payments p
        JOIN rentals r ON p.rental_id = r.rental_id
        JOIN users u ON r.user_id = u.user_id
        WHERE r.rental_id = %s
    """, (rental_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows




# ---------------- USERS ----------------

def get_all_users():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT user_id, first_name, last_name FROM users")
    users = cur.fetchall()
    cur.close()
    conn.close()
    return users
  
def get_admin_dashboard_stats():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM cars")
    total_cars = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM cars WHERE status='available'")
    available_cars = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM rentals")
    total_rentals = cur.fetchone()[0]

    cur.execute("""
        SELECT COALESCE(SUM(amount),0)
        FROM payments
        WHERE status='completed'
    """)
    total_income = cur.fetchone()[0]

    conn.close()

    return {
        "total_cars": total_cars,
        "available_cars": available_cars,
        "total_rentals": total_rentals,
        "total_income": total_income
    }

def get_user_dashboard_stats(user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT COUNT(*) FROM rentals WHERE user_id=%s
    """, (user_id,))
    my_rentals = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*) FROM rentals
        WHERE user_id=%s AND status='active'
    """, (user_id,))
    active_rentals = cur.fetchone()[0]

    cur.execute("""
        SELECT COALESCE(SUM(amount),0)
        FROM payments p
        JOIN rentals r ON p.rental_id = r.rental_id
        WHERE r.user_id=%s AND p.status='completed'
    """, (user_id,))
    my_payments = cur.fetchone()[0]

    conn.close()

    return {
        "my_rentals": my_rentals,
        "active_rentals": active_rentals,
        "my_payments": my_payments
    }

def get_user_rentals(user_id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT
            r.rental_id,
            r.start_date,
            r.end_date,
            r.total_price,
            r.status,

            c.name AS car_name,
            c.brand,

            COALESCE(SUM(p.amount), 0) AS paid
        FROM rentals r
        JOIN cars c ON r.car_id = c.car_id
        LEFT JOIN payments p ON p.rental_id = r.rental_id
        WHERE r.user_id = %s
        GROUP BY r.rental_id, c.name, c.brand
        ORDER BY r.rental_id DESC
    """, (user_id,))

    rentals = cur.fetchall()

    cur.close()
    conn.close()

    # محاسبه remaining در بک‌اند (نه توی template)
    for r in rentals:
        r["remaining"] = r["total_price"] - r["paid"]

    return rentals


# ---------------- AUTH ----------------

from werkzeug.security import generate_password_hash, check_password_hash

def create_user(first_name, last_name, email, password, phone_number, role="user"):
    conn = get_connection()
    cur = conn.cursor()
    hashed = generate_password_hash(password)
    cur.execute("""
        INSERT INTO users
        (first_name, last_name, email, hashed_password, phone_number, role)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (first_name, last_name, email, hashed, phone_number, role))
    conn.commit()
    cur.close()
    conn.close()

def verify_user(email, password):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT user_id, hashed_password, role FROM users WHERE email=%s
    """, (email,))
    row = cur.fetchone()
    conn.close()
    if row and check_password_hash(row[1], password):
        return {"user_id": row[0], "role": row[2]}
    return None

