from flask import Flask, make_response, request
from flask_jwt_extended import JWTManager
from sqlalchemy import and_

from source_common.eth_common import read_abi_bytecode, send_transaction
from source_common.configuration import FLASK_DEBUG, Configuration, WITH_BLOCKCHAIN, get_owner_keys, IS_DOCKER, get_web3
from source_common.models import CREATED, PENDING, database, Order, COURIER
from source_common.utils import request_get_id, role_check, error_response, request_get_address

application = Flask(__name__)
application.config.from_object(Configuration)
database.init_app(application)
jwt = JWTManager(application)

@application.route("/orders_to_deliver", methods = ["GET"])
@role_check(COURIER)
def orders_to_deliver():
    orders_query = (database.session.query(Order.id, Order.customer_email)
        .filter(Order.status == CREATED)
        .all()
    )
    res = {"orders": []}
    for order in orders_query:
        res["orders"].append({"id": order[0], "email": order[1]})
    
    return make_response(res, 200)

@application.route("/pick_up_order", methods = ["POST"])
@role_check(COURIER)
def pick_up_order():
    order_id, err = request_get_id()
    if err: 
        return err

    order = Order.query.filter(and_(Order.id == order_id, Order.status == CREATED)).first()
    if not order:
        return error_response("Invalid order id.", 400)
    
    courier_address = ""
    if WITH_BLOCKCHAIN:
        web3 = get_web3()
        courier_address, err = request_get_address("/pick_up_order")
        if err:
            return err
        try:
            abi, _ = read_abi_bytecode()
            del_contract = web3.eth.contract(abi = abi, address = order.public_bc_address)
            owner_address, owner_key = get_owner_keys()

            tx = del_contract.functions.pick_up_order(courier_address).build_transaction({
                "from": owner_address,
                "gasPrice": 21000,
                "nonce": web3.eth.get_transaction_count(owner_address)
            })
            tx["gas"] = web3.eth.estimate_gas(tx)
            send_transaction(tx, owner_key)
        except Exception as e:
            print(e, flush = True)
            return error_response("Transfer not complete.", 400)
    
    order.status = PENDING
    database.session.commit()
    
    return make_response("", 200)


if ( __name__ == "__main__" ):
    host_adr = "0.0.0.0" if IS_DOCKER else "127.0.0.1"
    application.run(host = host_adr, debug = FLASK_DEBUG, port = 5000)
