from flask import Flask, make_response, request
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from sqlalchemy import and_

from source_common.configuration import FLASK_DEBUG, IS_DOCKER, Configuration, WITH_BLOCKCHAIN, get_owner_keys, get_web3
from source_common.models import CREATED, PENDING, COMPLETE, database, Product, Category, ProductCategory, Order, OrderItem, CUSTOMER
from source_common.utils import request_get_address, request_get_id, role_check, error_response
from source_common.eth_common import read_abi_bytecode, send_transaction, create_and_deploy_contract

application = Flask(__name__)
application.config.from_object(Configuration)
database.init_app(application)
jwt = JWTManager(application)


@application.route("/search", methods=["GET"])
@role_check(CUSTOMER)
def search():
    product_name     = request.args.get("name", "")
    category_name    = request.args.get("category", "")
    res = {"categories": [], 'products': []}
    
    # like - case-sensitive search, ilike - case-insensitive search
    categories_query = (database.session.query(Category.name)
        .join(ProductCategory, ProductCategory.category_id == Category.id)
        .join(Product, Product.id == ProductCategory.product_id)
        .filter(and_(Product.name.like(f"%{product_name}%"), Category.name.like(f"%{category_name}%")))
        .distinct()
        .all()
    )
    for category in categories_query:
        res["categories"].append(category[0])

    products_query = (database.session.query(Product)
        .join(ProductCategory, ProductCategory.product_id == Product.id)
        .join(Category, Category.id == ProductCategory.category_id)
        .filter(and_(Product.name.like(f"%{product_name}%"), Category.name.like(f"%{category_name}%")))
        .distinct()
        .all()
    )
    for product in products_query:
        res["products"].append({
            "categories": [category.name for category in product.categories],
            "id": product.id,
            "name": product.name,
            "price": product.price
        })

    return make_response(res, 200)

@application.route("/order", methods=["POST"])
@role_check(CUSTOMER)
def order():
    new_request_items = request.json.get("requests")
    if new_request_items is None:
        return error_response(f"Field requests is missing.", 400)
    
    new_order_items = []
    products = {}
    total_cost = 0.0

    for line_number, item in enumerate(new_request_items):
        product_id = item.get("id")
        quantity   = item.get("quantity")

        if product_id is None:  
            return error_response(f"Product id is missing for request number {line_number}.", 400)
        if quantity is None:    
            return error_response(f"Product quantity is missing for request number {line_number}.", 400)
        if isinstance(product_id, int) == False or product_id <= 0:
            return error_response(f"Invalid product id for request number {line_number}.", 400)
        if isinstance(quantity, int) == False or quantity <= 0:
            return error_response(f"Invalid product quantity for request number {line_number}.", 400)
        
        if product_id not in products:
            temp_pro = Product.query.filter(Product.id == product_id).first()
            if temp_pro is None:
                return error_response(f"Invalid product for request number {line_number}.", 400)
            products[product_id] = temp_pro
        
        total_cost += products[product_id].price * quantity
        new_order_items.append([product_id, quantity])

    contract_address = None
    if WITH_BLOCKCHAIN:
        customer_address, err = request_get_address("/order", "Field address is missing.")
        if err:
            return err
        contract_address = create_and_deploy_contract(customer_address, int(total_cost * 100))

    new_order = Order(price = total_cost, status = CREATED, customer_email = get_jwt_identity(), public_bc_address = contract_address)
    database.session.add(new_order)
    database.session.flush()

    for item in new_order_items:
        new_order_item = OrderItem(order_id = new_order.id, product_id = item[0], quantity = item[1])
        database.session.add(new_order_item)
    database.session.commit()

    return make_response({"id": new_order.id}, 200)

@application.route("/status", methods=["GET"])
@role_check(CUSTOMER)
def status():
    orders_all = Order.query.filter(Order.customer_email == get_jwt_identity()).all()
    orders = {
    "orders": 
        [
            {
                "products": [
                    {
                        "categories": [category.name for category in item.product.categories],
                        "name": item.product.name,
                        "price": item.product.price,
                        "quantity": item.quantity
                    }
                    for item in order.order_items
                ],
                "price": order.price,
                "status": order.status,
                "timestamp": order.time_created.isoformat()
            }
            for order in orders_all
        ]
    }
    return make_response(orders, 200)

@application.route("/delivered", methods = ["POST"])
@role_check(CUSTOMER)
def delivered():
    order_id, err = request_get_id()
    if err:
        return err

    order = Order.query.filter(Order.id == order_id).first()
    if not order:
        return error_response(f"Invalid order id.", 400)
    if order.status == CREATED:
        return error_response(f"Delivery not complete.", 400)
    if order.status == COMPLETE:
        return error_response(f"Delivery already complete.", 400)

    # check: order belongs to customer
    if order.customer_email != get_jwt_identity():
        print(f"Order does not belong to this customer.", flush=True)
    
    if WITH_BLOCKCHAIN:
        web3 = get_web3()
        abi, _ = read_abi_bytecode()
        owner_address, owner_key = get_owner_keys()
        
        del_contract = web3.eth.contract(abi = abi, address = order.public_bc_address)
        try:
            tx = del_contract.functions.delivered().build_transaction({
                "from": owner_address,
                "gasPrice": 21000,
                "nonce": web3.eth.get_transaction_count(owner_address)
            })
            tx["gas"] = web3.eth.estimate_gas(tx)
            send_transaction(tx, owner_key)
        except Exception as e:
            print(e, flush = True)
            return error_response("Error while processing blockchain transaction.", 500)

    order.status = COMPLETE
    database.session.commit()
    
    return make_response("", 200)

@application.route("/generate_invoice", methods = ["POST"])
@role_check(CUSTOMER)
def generate_invoice():
    order_id, err = request_get_id()
    if err:
        return err
    
    order = Order.query.filter(Order.id == order_id).first()
    if not order:
        return error_response(f"Invalid order id.", 400)
    
    customer_address, err = request_get_address("/generate_invoice")
    if err:
        return err
    
    # check: order belongs to customer
    if order.customer_email != get_jwt_identity():
        print(f"Order does not belong to this customer.", flush=True)
    
    web3 = get_web3()
    abi, _ = read_abi_bytecode()
    del_contract = web3.eth.contract(abi = abi, address = order.public_bc_address)
    contract_stage = del_contract.functions.get_stage().call()
    if contract_stage != "CREATED":
        return error_response(f"Transfer already complete.", 400)
    try:
        tx = del_contract.functions.invoice().build_transaction({
            "from": customer_address,
            "gasPrice": 21000,
            "nonce": web3.eth.get_transaction_count(customer_address),
            "value": int(order.price * 100)
        })
        tx["gas"] = web3.eth.estimate_gas(tx)
    except Exception as e:
        print(e, flush = True)
        return error_response(str(e), 400)

    database.session.commit()
    
    return make_response({"invoice": tx}, 200)


if ( __name__ == "__main__" ):
    host_adr = "0.0.0.0" if IS_DOCKER else "127.0.0.1"
    application.run(host = host_adr, debug = FLASK_DEBUG, port = 5000)
