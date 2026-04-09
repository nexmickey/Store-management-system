import csv
import io
import os
import time
from flask import Flask, make_response, request
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate, init, migrate, upgrade
from sqlalchemy import and_, asc, desc, or_, text, func
from helper import helper_bp

from source_common.configuration import FLASK_DEBUG, IS_DOCKER, Configuration
from source_common.models import COMPLETE, CREATED, PENDING, Order, OrderItem, database, Product, Category, ProductCategory, OWNER
from source_common.utils import role_check, error_response
from source_common.eth_common import helper_eth_bp

application = Flask(__name__)
application.config.from_object(Configuration)
database.init_app(application)
migrate_ee = Migrate(application, database)

jwt = JWTManager(application)
application.register_blueprint(helper_bp)
application.register_blueprint(helper_eth_bp)

@application.route("/update", methods=["POST"])
@role_check(OWNER)
def product_update():
    if "file" not in request.files:
        return error_response(f"Field file is missing.", 400)
    
    reader = csv.reader(io.TextIOWrapper(request.files.get("file").stream, encoding='utf-8'))

    products = []
    product_names = set()
    for product in (database.session.query(Product.name).all()):
        product_names.add(product[0])

    for line_num, row in enumerate(reader):
        # Skip empty lines
        if not row:
            continue

        if len(row) != 3:
            return error_response(f"Incorrect number of values on line {line_num}.", 400)
        
        categories_str, name, price_str = row
        if not name.strip() or not categories_str.strip() or not price_str.strip():
            print(f"Line {line_num} has empty fields.", flush=True)

        try:
            price = float(price_str)
            if price <= 0: 
                raise ValueError
        except ValueError:
            return error_response(f"Incorrect price on line {line_num}.", 400)
        
        # Check if product name already exists
        if name in product_names:
            return error_response(f"Product {name} already exists.", 400)

        product_names.add(name)
        products.append((name, price, categories_str.split("|")))

    if not products:
        return error_response("", 200)

    category_cache = {}
    for category in Category.query.all():
        category_cache[category.name] = category

    try:
        for name, price, category_list in products:
            new_product = Product(name=name, price=price)
            database.session.add(new_product)
            database.session.flush()

            for cat_name in category_list:
                if cat_name not in category_cache:
                    new_category = Category(name=cat_name)
                    database.session.add(new_category)
                    database.session.flush()
                    category_cache[cat_name] = new_category
                
                pc = ProductCategory(product_id=new_product.id, category_id=category_cache[cat_name].id)
                database.session.add(pc)

        database.session.commit()
    except Exception as e:
        database.session.rollback()
        return error_response(f"Database error: {str(e)}", 400)
    return make_response("", 200)

@application.route("/product_statistics", methods=["GET"])
@role_check(OWNER)
def product_statistics():
    product_stats = {}
    sold_query = (database.session.query(Product.name, func.sum(OrderItem.quantity))
        .join(OrderItem, Product.id == OrderItem.product_id)
        .join(Order, Order.id == OrderItem.order_id)
        .filter(Order.status == COMPLETE)
        .group_by(Product.name)
        .all()
    )
    for name, quantity in sold_query:
        product_stats[name] = [int(quantity), 0]

    waiting_query = (database.session.query(Product.name, func.sum(OrderItem.quantity))
        .join(OrderItem, Product.id == OrderItem.product_id)
        .join(Order, Order.id == OrderItem.order_id)
        .filter(or_(Order.status == CREATED, Order.status == PENDING))
        .group_by(Product.name)
        .all()
    )
    for name, quantity in waiting_query:
        if name not in product_stats:
            product_stats[name] = [0, int(quantity)]
        else:
            product_stats[name][1] = int(quantity)

    res = [{"name": name, "sold": counts[0], "waiting": counts[1]} for name, counts in product_stats.items()]

    return make_response({"statistics": res}, 200)


@application.route("/category_statistics", methods=["GET"])
@role_check(OWNER)
def category_statistics():
    category_dict = {}
    for category in (database.session.query(Category.name).all()):
        category_dict[category.name] = 0

    category_query = (database.session.query(Category.name, func.coalesce(func.sum(OrderItem.quantity), 0))
        .join(ProductCategory, Category.id == ProductCategory.category_id)
        .join(Product, ProductCategory.product_id == Product.id)
        .join(OrderItem, OrderItem.product_id == Product.id)
        .join(Order, Order.id == OrderItem.order_id)
        .filter(Order.status == COMPLETE)
        .group_by(Category.id, Category.name)
        .all()
    )
    for category in category_query:
        category_dict[category[0]] = int(category[1])
    category_arr = [(name, quantity) for name, quantity in category_dict.items()]
    sorted_categories = sorted(category_arr, key=lambda x: (-x[1], x[0]))
    return make_response({"statistics": [name for name, _ in sorted_categories]}, 200)


def wait_for_db(max_retries=10):
    retries = 0
    while retries < max_retries:
        try:
            database.session.execute(text('SELECT 1'))
            print("[+] Database is online!")
            return True
        except Exception:
            retries += 1
            print(f"[-] Database not ready. Tries {retries}/{max_retries}")
            time.sleep(2)
    
    raise Exception("Could not connect to the database.")

# Create all tables
@application.cli.command("init-db")
def init_db():
    print("[+] Initializing database...")
    try:
        wait_for_db()

        # database.create_all()

        if not os.path.exists("migrations/env.py"):
            print("[*] Migrations folder missing. Initializing...")
            init()
            migrate(message="Initial migration")
            upgrade()
        else:
            print("[*] Migrations folder found. Upgrading schema...")
            upgrade()

        print("[+] Database initialized successfully!")
        
    except Exception as error:
        print(f"[-] Failed to initialize database: {error}")

        
if (__name__ == "__main__"):
    host_adr = "0.0.0.0" if IS_DOCKER else "127.0.0.1"
    application.run(host = host_adr, debug = FLASK_DEBUG, port = 5000)



