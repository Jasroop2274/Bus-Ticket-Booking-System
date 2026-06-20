# app.py
from flask import Flask
from db_mysql import init_db, close_db
from customer_routes import customer_bp
from admin_routes import admin_bp


def create_app():
    app = Flask(__name__)
    app.secret_key = "change_this_secret_key"

    # DB teardown
    app.teardown_appcontext(close_db)

    # Register blueprints
    app.register_blueprint(customer_bp)
    app.register_blueprint(admin_bp)

    # Initialize DB (tables + seed)
    with app.app_context():
        init_db()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)