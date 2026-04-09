from flask_sqlalchemy import SQLAlchemy

MAX_FIELD_LENGTH = 256

database = SQLAlchemy()

CUSTOMER = "customer"
COURIER  = "courier"
OWNER    = "owner"

class ProductCategory(database.Model):
    id          = database.Column(database.Integer, primary_key = True)
    product_id  = database.Column(database.Integer, database.ForeignKey("product.id"), nullable = False)
    category_id = database.Column(database.Integer, database.ForeignKey("category.id"), nullable = False)


class OrderItem(database.Model):
    order_id    = database.Column(database.Integer, database.ForeignKey("order.id"), primary_key = True)
    product_id  = database.Column(database.Integer, database.ForeignKey("product.id"), primary_key = True)
    quantity    = database.Column(database.Integer, nullable = False)

    order       = database.relationship("Order", back_populates="order_items")
    product     = database.relationship("Product", back_populates="orders_items")

    def __repr__(self):
        return f"[OrderItem {self.order_id}, {self.product_id}, {self.quantity}]"


class Product(database.Model):
    id          = database.Column(database.Integer, primary_key = True)
    name        = database.Column(database.String(MAX_FIELD_LENGTH), nullable = False, unique = True)
    price       = database.Column(database.Float, nullable = False)

    categories   = database.relationship("Category", secondary = ProductCategory.__table__, back_populates = "products")
    orders_items = database.relationship("OrderItem", back_populates="product")

    def __repr__(self):
        return f"[Product {self.id}, {self.name}, {self.price}, {self.dummy1 == None}]"


class Category(database.Model):
    id       = database.Column(database.Integer, primary_key = True)
    name     = database.Column(database.String(MAX_FIELD_LENGTH), nullable = False, unique = True)

    products   = database.relationship("Product", secondary = ProductCategory.__table__, back_populates = "categories")

    def __repr__(self):
        return f"[Category {self.id}, {self.name}]"


CREATED = "CREATED"
PENDING = "PENDING"
COMPLETE = "COMPLETE"

class Order(database.Model):
    id             = database.Column(database.Integer, primary_key = True)
    price          = database.Column(database.Float, nullable = False)
    status         = database.Column(database.String(MAX_FIELD_LENGTH), nullable = False)
    time_created   = database.Column(database.DateTime, nullable = False, server_default=database.func.now())
    customer_email = database.Column(database.String(MAX_FIELD_LENGTH), nullable = False)

    public_bc_address = database.Column(database.String(MAX_FIELD_LENGTH), nullable = True)

    order_items = database.relationship("OrderItem", back_populates="order")

    def __repr__(self):
        return f"[Order {self.id}, {self.price}, {self.status}, {self.time_created}, {self.customer_email}]"
    