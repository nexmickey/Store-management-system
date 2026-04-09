from flask import jsonify, request
from flask_jwt_extended import get_jwt, jwt_required
from functools import wraps

from .configuration import get_web3

MAX_FIELD_LENGTH = 256

def error_response(message, status_code = 400):
    return jsonify({"message": message}), status_code

def check_field_max_length(field):
    if len(field) > MAX_FIELD_LENGTH:
        return False
    return True

def role_check(role):
    def decorator(function):
        @jwt_required()
        @wraps(function)
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            if (role == claims["roles"]):
                return function(*args, **kwargs)
            else: # Invalid role
                return jsonify({"msg": "Missing Authorization Header"}), 401

        return wrapper

    return decorator

def request_get_id():
    id = request.json.get("id")
    if id is None:
        return None, error_response("Missing order id.", 400)
    if isinstance(id, int) == False or id <= 0:
        return None, error_response("Invalid order id.", 400)
    return id, None

def request_get_address(path = "", missing_message_text = "Missing address."):
    address = request.json.get("address")
    if address is None or isinstance(address, str) == False:
        return None, error_response(missing_message_text, 400)
    
    if len(address) == 0 and path != "/generate_invoice":
        return None, error_response(missing_message_text, 400)
    
    web3 = get_web3()
    if web3.is_address(address) == False:
        return None, error_response("Invalid address.", 400)
    return address, None
