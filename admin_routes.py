# admin_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, session
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


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def is_admin():
    return session.get("user_id") and session.get("role") == "admin"


@admin_bp.before_request
def check_admin():
    if not is_admin() and not request.path.startswith("/admin/login-bypass"):
        return redirect(url_for("customer.login"))


@admin_bp.route("/")
def dashboard():
    return render_template("admin_dashboard.html")


@admin_bp.route("/buses", methods=["GET", "POST"])
def buses():
    conn = get_db()

    if request.method == "POST":
        bus_no = request.form["bus_no"]
        operator = request.form["operator"]
        total_seats = request.form["total_seats"]

        if bus_no and operator and total_seats:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO buses (bus_no, operator, total_seats) VALUES (%s, %s, %s)",
                (bus_no, operator, int(total_seats)),
            )
            conn.commit()
            cur.close()

    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM buses ORDER BY id")
    buses = cur.fetchall()
    cur.close()

    return render_template("admin_buses.html", buses=buses)


@admin_bp.route("/trips", methods=["GET", "POST"])
def trips():
    conn = get_db()

    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, bus_no, operator FROM buses ORDER BY id")
    buses = cur.fetchall()
    cur.close()

    if request.method == "POST":
        bus_id = request.form["bus_id"]
        source = request.form["source"]
        destination = request.form["destination"]
        travel_date = request.form["travel_date"]   # from calendar, YYYY-MM-DD
        departure_time = request.form["departure_time"]
        fare = request.form["fare"]

        if bus_id and source and destination and travel_date and departure_time and fare:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO trips (bus_id, source, destination, travel_date, departure_time, fare)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (int(bus_id), source, destination, travel_date, departure_time, float(fare)),
            )
            conn.commit()
            cur.close()

    cur = conn.cursor(dictionary=True)
    cur.execute(
        """
        SELECT t.id, b.bus_no, b.operator, t.source, t.destination,
               t.travel_date, t.departure_time, t.fare
        FROM trips t
        JOIN buses b ON t.bus_id = b.id
        ORDER BY t.travel_date, t.departure_time
        """
    )
    trips = cur.fetchall()
    cur.close()

    for t in trips:
        try:
            t["travel_date"] = datetime.strptime(str(t["travel_date"]), "%Y-%m-%d").strftime("%d-%m-%Y")
        except Exception:
            pass

    return render_template("admin_trips.html", buses=buses, trips=trips, cities=CITY_LIST)