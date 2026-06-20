# customer_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from db_mysql import get_db


CITY_LIST = [
    "Delhi", "Dehradun", "Meerut", "Haridwar", "Kolkata",
    "Mumbai", "Noida", "Ghaziabad", "Lucknow", "Kanpur",
    "Agra", "Varanasi", "Jaipur", "Chandigarh", "Amritsar",
    "Patna", "Ranchi", "Bhopal", "Indore", "Ahmedabad",
    "Surat", "Pune", "Nagpur", "Hyderabad", "Bengaluru",
    "Chennai", "Kochi", "Bhubaneswar", "Guwahati", "Prayagraj"
]


customer_bp = Blueprint("customer", __name__)


@customer_bp.route("/")
def index():
    return render_template("index.html", cities=CITY_LIST)


@customer_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        if not name or not email or not password:
            return render_template("register.html", error="All fields are required.")

        conn = get_db()
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO users (name, email, password_hash, role) VALUES (%s, %s, %s, %s)",
                (name, email, generate_password_hash(password), "user"),
            )
            conn.commit()
        except Exception:
            conn.rollback()
            cur.close()
            return render_template("register.html", error="Email already registered.")
        cur.close()
        return redirect(url_for("customer.login"))
    return render_template("register.html")


@customer_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["role"] = user["role"]
            return redirect(url_for("customer.index"))
        else:
            return render_template("login.html", error="Invalid email or password.")
    return render_template("login.html")


@customer_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("customer.index"))


@customer_bp.route("/search", methods=["POST"])
def search():
    source = request.form["source"]
    destination = request.form["destination"]
    db_date = request.form["date"]

    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        """
        SELECT t.*, b.bus_no, b.operator, b.total_seats,
        (b.total_seats - IFNULL(
            (SELECT COALESCE(SUM(seats_booked),0) FROM bookings
             WHERE trip_id = t.id AND status = 'CONFIRMED'), 0)
        ) AS available_seats
        FROM trips t
        JOIN buses b ON t.bus_id = b.id
        WHERE t.source = %s AND t.destination = %s AND t.travel_date = %s
        """,
        (source, destination, db_date),
    )
    trips = cur.fetchall()
    cur.close()

    try:
        display_date = datetime.strptime(db_date, "%Y-%m-%d").strftime("%d-%m-%Y")
    except ValueError:
        display_date = db_date

    return render_template(
        "search_results.html",
        trips=trips,
        source=source,
        destination=destination,
        date=display_date,
    )


@customer_bp.route("/book/<int:trip_id>", methods=["GET", "POST"])
def book(trip_id):
    if "user_id" not in session:
        return redirect(url_for("customer.login"))

    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        """
        SELECT t.*, b.bus_no, b.operator, b.total_seats,
        (b.total_seats - IFNULL(
            (SELECT COALESCE(SUM(seats_booked),0) FROM bookings
             WHERE trip_id = t.id AND status = 'CONFIRMED'), 0)
        ) AS available_seats
        FROM trips t
        JOIN buses b ON t.bus_id = b.id
        WHERE t.id = %s
        """,
        (trip_id,),
    )
    trip = cur.fetchone()
    cur.close()

    if not trip:
        return "Trip not found", 404

    if request.method == "POST":
        seats = int(request.form["seats"])
        if seats <= 0:
            return render_template("book.html", trip=trip, error="Seats must be positive.")
        if seats > trip["available_seats"]:
            return render_template("book.html", trip=trip, error="Not enough seats available.")

        total_amount = seats * float(trip["fare"])
        booking_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO bookings
            (user_id, trip_id, seats_booked, total_amount, booking_time, status)
            VALUES (%s, %s, %s, %s, %s, 'CONFIRMED')
            """,
            (session["user_id"], trip_id, seats, total_amount, booking_time),
        )
        conn.commit()
        cur.close()
        return redirect(url_for("customer.my_bookings"))

    return render_template("book.html", trip=trip)


@customer_bp.route("/my_bookings")
def my_bookings():
    if "user_id" not in session:
        return redirect(url_for("customer.login"))

    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        """
        SELECT bk.id, bk.seats_booked, bk.total_amount, bk.booking_time, bk.status,
               t.source, t.destination, t.travel_date, t.departure_time,
               b.bus_no, b.operator
        FROM bookings bk
        JOIN trips t ON bk.trip_id = t.id
        JOIN buses b ON t.bus_id = b.id
        WHERE bk.user_id = %s
        ORDER BY bk.booking_time DESC
        """,
        (session["user_id"],),
    )
    rows = cur.fetchall()
    cur.close()

    bookings = []
    for r in rows:
        try:
            d = datetime.strptime(str(r["travel_date"]), "%Y-%m-%d")
            r["travel_date"] = d.strftime("%d-%m-%Y")
        except Exception:
            pass
        try:
            bt = datetime.strptime(str(r["booking_time"]), "%Y-%m-%d %H:%M:%S")
            r["booking_time"] = bt.strftime("%d-%m-%Y %H:%M:%S")
        except Exception:
            pass
        bookings.append(r)

    return render_template("my_bookings.html", bookings=bookings)