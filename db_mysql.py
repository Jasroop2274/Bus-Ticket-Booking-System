# db_mysql.py
import mysql.connector
from mysql.connector import Error
from flask import g
from werkzeug.security import generate_password_hash
from datetime import datetime

DB_CONFIG = {
    "host": "localhost",
    "user": "root",          # or whatever user you use in MySQL Workbench
    "password": "root",
    "database": "bus_booking",
}

def get_db():
    """Get a MySQL connection stored on Flask's g object."""
    conn = getattr(g, "_mysql_conn", None)
    if conn is None or not conn.is_connected():
        conn = mysql.connector.connect(**DB_CONFIG)
        g._mysql_conn = conn
    return conn


def close_db(exception=None):
    conn = getattr(g, "_mysql_conn", None)
    if conn is not None and conn.is_connected():
        conn.close()


def init_db():
    """Create tables and seed initial data (buses, trips, admin user)."""
    conn = mysql.connector.connect(**DB_CONFIG)
    cur = conn.cursor()

    # users table with role
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            role VARCHAR(20) NOT NULL DEFAULT 'user'
        ) ENGINE=InnoDB
    """)

    # buses
    cur.execute("""
        CREATE TABLE IF NOT EXISTS buses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            bus_no VARCHAR(20) NOT NULL,
            operator VARCHAR(100) NOT NULL,
            total_seats INT NOT NULL
        ) ENGINE=InnoDB
    """)

    # trips
    cur.execute("""
        CREATE TABLE IF NOT EXISTS trips (
            id INT AUTO_INCREMENT PRIMARY KEY,
            bus_id INT NOT NULL,
            source VARCHAR(100) NOT NULL,
            destination VARCHAR(100) NOT NULL,
            travel_date DATE NOT NULL,
            departure_time VARCHAR(10) NOT NULL,
            fare DECIMAL(10,2) NOT NULL,
            FOREIGN KEY (bus_id) REFERENCES buses(id)
                ON DELETE CASCADE ON UPDATE CASCADE
        ) ENGINE=InnoDB
    """)

    # bookings
    cur.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            trip_id INT NOT NULL,
            seats_booked INT NOT NULL,
            total_amount DECIMAL(10,2) NOT NULL,
            booking_time DATETIME NOT NULL,
            status VARCHAR(20) NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
                ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (trip_id) REFERENCES trips(id)
                ON DELETE CASCADE ON UPDATE CASCADE
        ) ENGINE=InnoDB
    """)

    # seed buses/trips
    cur.execute("SELECT COUNT(*) FROM buses")
    if cur.fetchone()[0] == 0:
        cur.execute(
            "INSERT INTO buses (bus_no, operator, total_seats) VALUES (%s, %s, %s)",
            ("DL01AB1234", "GEU Travels", 40),
        )
        cur.execute(
            "INSERT INTO buses (bus_no, operator, total_seats) VALUES (%s, %s, %s)",
            ("DL02CD5678", "Campus Express", 30),
        )

    cur.execute("SELECT COUNT(*) FROM trips")
    if cur.fetchone()[0] == 0:
        cur.execute(
            "INSERT INTO trips (bus_id, source, destination, travel_date, departure_time, fare) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (1, "Dehradun", "Delhi", "2026-04-01", "09:00", 500.0),
        )
        cur.execute(
            "INSERT INTO trips (bus_id, source, destination, travel_date, departure_time, fare) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (2, "Dehradun", "Delhi", "2026-04-01", "15:00", 550.0),
        )

    # seed admin user
    cur.execute("SELECT COUNT(*) FROM users WHERE email = %s", ("admin@bus.com",))
    if cur.fetchone()[0] == 0:
        admin_pw = generate_password_hash("admin123")
        cur.execute(
            "INSERT INTO users (name, email, password_hash, role) VALUES (%s, %s, %s, %s)",
            ("System Admin", "admin@bus.com", admin_pw, "admin"),
        )

    conn.commit()
    cur.close()
    conn.close()