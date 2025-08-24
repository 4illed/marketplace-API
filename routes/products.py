from flask import Blueprint, request, jsonify, abort, current_app
import psycopg2
from psycopg2.extras import RealDictCursor

products_bp = Blueprint("products", __name__, url_prefix="/products")


def get_db_connection():
    """
    Connect to the PostgreSQL database and return a connection object.
    :return: psycopg2.extensions.connection
    """
    conn = psycopg2.connect(
        dbname=current_app.config["DB_NAME"],
        user=current_app.config["DB_USER"],
        password=current_app.config["DB_PASSWORD"],
        host=current_app.config.get("DB_HOST", "localhost"),
    )
    return conn


@products_bp.route("", methods=["GET"])
def get_products():
    """
    Retrieve a list of products based on the provided query parameters.
    :return: JSON response with a list of products
    """
    category = request.args.get("category")
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)

    where_clauses = []
    params = []
    if category:
        where_clauses.append("category = %s")
        params.append(category)
    if min_price is not None:
        where_clauses.append("price >= %s")
        params.append(min_price)
    if max_price is not None:
        where_clauses.append("price <= %s")
        params.append(max_price)

    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(f"SELECT * FROM products {where_sql};", params)
            products = cur.fetchall()
    finally:
        conn.close()

    # Convert Decimal prices to float
    for p in products:
        p["price"] = float(p["price"])
    return jsonify(products), 200


@products_bp.route("/<int:product_id>", methods=["GET"])
def get_product(product_id):
    """
    Retrieve a product by its ID
    """
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM products WHERE id = %s;", (product_id,))
            product = cur.fetchone()
            if not product:
                abort(404, description="Product not found")
    finally:
        conn.close()
    product["price"] = float(product["price"])
    return jsonify(product), 200


@products_bp.route("", methods=["POST"])
def create_product():
    """
    Create a new product
    """
    data = request.get_json()
    required_fields = ["name", "description", "price", "category"]
    if not data or not all(field in data for field in required_fields):
        abort(400, description="Missing required fields")

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO products (name, description, price, category)
                VALUES (%s, %s, %s, %s)
                RETURNING id, name, description, price, category;
                """,
                (
                    data["name"],
                    data["description"],
                    float(data["price"]),
                    data["category"],
                ),
            )
            product = cur.fetchone()
            conn.commit()
    finally:
        conn.close()

    # Convert Decimal price to float
    product = {
        "id": product[0],
        "name": product[1],
        "description": product[2],
        "price": float(product[3]),
        "category": product[4],
    }
    return jsonify(product), 201


@products_bp.route("/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    """
    Update an existing product by its ID
    """
    data = request.get_json()
    if not data:
        abort(400, description="No update data provided")

    set_clauses = []
    params = []
    for field in ["name", "description", "price", "category"]:
        if field in data:
            set_clauses.append(f"{field} = %s")
            params.append(float(data[field]) if field == "price" else data[field])

    if not set_clauses:
        abort(400, description="No valid fields to update")

    params.append(product_id)
    set_sql = ", ".join(set_clauses)

    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                f"UPDATE products SET {set_sql} WHERE id = %s RETURNING id, name, description, price, category;",
                params,
            )
            product = cur.fetchone()
            if not product:
                abort(404, description="Product not found")
            conn.commit()
    finally:
        conn.close()

    product["price"] = float(product["price"])
    return jsonify(product), 200


@products_bp.route("/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    """
    Delete a product by its ID
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM products WHERE id = %s RETURNING id;", (product_id,)
            )
            result = cur.fetchone()
            if not result:
                abort(404, description="Product not found")
            conn.commit()
    finally:
        conn.close()
    return jsonify({"message": "Product deleted"}), 200
