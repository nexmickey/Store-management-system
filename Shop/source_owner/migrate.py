
from flask import Flask
from flask_migrate import Migrate
from source_common.models import database
from source_common.configuration import Configuration

def create_app():
    app = Flask(__name__)
    app.config.from_object(Configuration)
    database.init_app(app)
    from source_common.models import Product, Category, ProductCategory, Order, OrderItem
    Migrate(app, database)
    return app

application = create_app()