from flask import Blueprint, jsonify
from sqlalchemy import text

from source_common.models import Category, Order, Product, ProductCategory, OrderItem, Order, database

helper_bp = Blueprint("helper", __name__)

@helper_bp.route("/check_alive", methods=["GET"])
def check_alive():
    return "Alive"

@helper_bp.route("/all_products", methods=["GET"])
def all_products():
    products = Product.query.all()
    return jsonify([str(product) for product in products])

@helper_bp.route("/all_categories", methods=["GET"])
def all__categories():
    categories = Category.query.all()
    return jsonify([str(category) for category in categories])

@helper_bp.route("/all_orders", methods=["GET"])
def all_orders():
    orders = Order.query.all()
    return jsonify([str(order) for order in orders])

@helper_bp.route("/delete_data", methods=["DELETE"])
def delete_data():
    database.session.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))

    OrderItem.query.delete()
    Order.query.delete()
    ProductCategory.query.delete()
    Category.query.delete()
    Product.query.delete()

    for table in ["product_category", "category", "product", "order", "order_item"]:
        query = text(f"ALTER TABLE `{table}` AUTO_INCREMENT = 1;")
        database.session.execute(query)

    database.session.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
    database.session.commit()
    return "Deleted all data"
