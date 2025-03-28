from flask import Blueprint, request, jsonify, abort, current_app
import psycopg2
from psycopg2.extras import RealDictCursor

data_bp = Blueprint("data", __name__, url_prefix="/data")


def get_db_connection():
    conn = psycopg2.connect(
        dbname=current_app.config["DB_NAME"],
        user=current_app.config["DB_USER"],
        password=current_app.config["DB_PASSWORD"],
        host=current_app.config.get("DB_HOST", "localhost"),
    )
    return conn


# USERS ENDPOINTS


@data_bp.route("/users", methods=["GET"])
def get_users():
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM users;")
            users = cur.fetchall()
    finally:
        conn.close()
    return jsonify(users), 200


@data_bp.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM users WHERE id = %s;", (user_id,))
            user = cur.fetchone()
            if not user:
                abort(404, description="User not found")
    finally:
        conn.close()
    return jsonify(user), 200


@data_bp.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
    required_fields = ["name", "email"]
    if not data or not all(field in data for field in required_fields):
        abort(400, description="Missing required fields: name and email")

    name = data["name"]
    email = data["email"]
    address = data.get("address")
    phone = data.get("phone")

    conn = get_db_connection()
    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    INSERT INTO users (name, email, address, phone)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id, name, email, address, phone;
                    """,
                    (name, email, address, phone),
                )
                user = cur.fetchone()
    except psycopg2.Error as e:
        conn.rollback()
        abort(500, description=str(e))
    finally:
        conn.close()
    return jsonify(user), 201


@data_bp.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    data = request.get_json()
    if not data:
        abort(400, description="No update data provided")

    set_clauses = []
    params = []
    for field in ["name", "email", "address", "phone"]:
        if field in data:
            set_clauses.append(f"{field} = %s")
            params.append(data[field])

    if not set_clauses:
        abort(400, description="No valid fields to update")

    params.append(user_id)
    set_sql = ", ".join(set_clauses)

    conn = get_db_connection()
    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    f"UPDATE users SET {set_sql} WHERE id = %s RETURNING id, name, email, address, phone;",
                    params,
                )
                user = cur.fetchone()
                if not user:
                    abort(404, description="User not found")
    finally:
        conn.close()
    return jsonify(user), 200


@data_bp.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    conn = get_db_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM users WHERE id = %s RETURNING id;", (user_id,))
                result = cur.fetchone()
                if not result:
                    abort(404, description="User not found")
    except psycopg2.Error as e:
        conn.rollback()
        abort(500, description=str(e))
    finally:
        conn.close()
    return jsonify({"message": "User deleted"}), 200
