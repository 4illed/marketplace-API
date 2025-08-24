from flask import Flask
from routes.products import products_bp
from routes.orders import orders_bp
from routes.data import data_bp

app = Flask(__name__)

# Configure PostgreSQL connection parameters
app.config["DB_NAME"] = "your_db_name"
app.config["DB_USER"] = "your_db_user"
app.config["DB_PASSWORD"] = "your_db_password"
app.config["DB_HOST"] = "localhost"

app.register_blueprint(products_bp)
app.register_blueprint(orders_bp)
app.register_blueprint(data_bp)

if __name__ == "__main__":
    app.run(debug=True)
