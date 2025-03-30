from flask import Blueprint, request, jsonify, abort, current_app
from psycopg2.extras import RealDictCursor
import psycopg2

orders_bp = Blueprint("orders", __name__, url_prefix="/orders")


def get_db_connection():
    """
    Establish a connection to the PostgreSQL database.
    :return: A psycopg2 connection object.
    """
    conn = psycopg2.connect(
        dbname=current_app.config["DB_NAME"],
        user=current_app.config["DB_USER"],
        password=current_app.config["DB_PASSWORD"],
        host=current_app.config.get("DB_HOST", "localhost"),
    )
    return conn


@orders_bp.route("", methods=["POST"])
def create_order():
    """
    Create a new order in the database.
    """
    data = request.get_json()
    # Expecting a JSON with "user_id" and "order_items" (a non-empty list)
    if not data or "user_id" not in data or "order_items" not in data:
        abort(400, description="Missing required fields: user_id or order_items")

    user_id = data["user_id"]
    status = data.get("status", "новый")
    order_items = data["order_items"]

    if not isinstance(order_items, list) or not order_items:
        abort(400, description="order_items must be a non-empty list")

    conn = get_db_connection()
    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Create new order with current timestamp (NOW())
                cur.execute(
                    """
                    INSERT INTO orders (user_id, order_date, status)
                    VALUES (%s, NOW(), %s)
                    RETURNING id, user_id, order_date, status;
                    """,
                    (user_id, status),
                )
                order = cur.fetchone()
                order_id = order["id"]

                inserted_items = []
                for item in order_items:
                    # each order item must include product_id, quantity, and price
                    if (
                        "product_id" not in item
                        or "quantity" not in item
                        or "price" not in item
                    ):
                        abort(
                            400,
                            description="Each order item must have product_id, quantity, and price",
                        )
                    cur.execute(
                        """
                        INSERT INTO order_items (order_id, product_id, quantity, price)
                        VALUES (%s, %s, %s, %s)
                        RETURNING id, order_id, product_id, quantity, price;
                        """,
                        (
                            order_id,
                            item["product_id"],
                            item["quantity"],
                            float(item["price"]),
                        ),
                    )
                    inserted_item = cur.fetchone()
                    inserted_item["price"] = float(inserted_item["price"])
                    inserted_items.append(inserted_item)

                order["order_items"] = inserted_items
        return jsonify(order), 201
    except Exception as e:
        conn.rollback()
        abort(500, description=str(e))
    finally:
        conn.close()


@orders_bp.route("/<int:order_id>", methods=["GET"])
def get_order(order_id):
    """
    Get an order by its ID.
    """
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM orders WHERE id = %s;", (order_id,))
            order = cur.fetchone()
            if not order:
                abort(404, description="Order not found")
            cur.execute("SELECT * FROM order_items WHERE order_id = %s;", (order_id,))
            order_items = cur.fetchall()
            for item in order_items:
                item["price"] = float(item["price"])
            order["order_items"] = order_items
        return jsonify(order), 200
    finally:
        conn.close()

@orders_bp.route("/<int:order_id>/status", methods=["PATCH"])
def update_order_status(order_id):
    """
    Update the status of an order by its ID.
    """
    data = request.get_json()
    if not data or "status" not in data:
        abort(400, description="Status is required")
    
    valid_statuses = ["новый", "в обработке", "выполнен"]
    if data["status"] not in valid_statuses:
        abort(400, description=f"Invalid status. Must be one of: {valid_statuses}")
    
    conn = get_db_connection()
    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    UPDATE orders SET status = %s 
                    WHERE id = %s 
                    RETURNING id, status;
                    """,
                    (data["status"], order_id),
                )
                result = cur.fetchone()
                if not result:
                    abort(404, description="Order not found")
    finally:
        conn.close()
    
    return jsonify(result), 200