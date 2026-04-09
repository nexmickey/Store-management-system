from datetime import timedelta
import os
from web3 import Account, HTTPProvider, Web3
import json

def read_file(path):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(current_dir, path)
    with open(full_path, "r") as file:
        return file.read()

web3 = None

DATABASE_URL        = os.environ.get("DATABASE_URL", "localhost")
DATABASE_USERNAME   = os.environ.get("DATABASE_USERNAME", "root")
DATABASE_PASSWORD   = os.environ.get("DATABASE_PASSWORD", "root")
DATABASE_NAME       = os.environ.get("DATABASE_NAME", "shops")
DATABASE_PORT       = os.environ.get("DATABASE_PORT", "3306")
FLASK_DEBUG         = os.environ.get("FLASK_DEBUG", "true").lower() == "true"
JWT_SECRET_KEY      = os.environ.get("JWT_SECRET_KEY", "JWT_SECRET_DEV_KEY")
IS_DOCKER           = os.environ.get("IS_DOCKER", "false").lower() == "true"


BLOCKCHAIN_URL      = os.environ.get("BLOCKCHAIN_URL", "http://127.0.0.1:8545")
WITH_BLOCKCHAIN     = os.environ.get("WITH_BLOCKCHAIN", "false").lower() == "true"

owner_address     = None
owner_private_key = ""

if WITH_BLOCKCHAIN:
    web3              = Web3(HTTPProvider(BLOCKCHAIN_URL))
    keys              = json.loads(read_file("owner_keys.json"))
    owner_address     = web3.to_checksum_address(keys["address"])
    owner_private_key = Account.decrypt(keys, "my_very_cool_password").hex()

def get_web3():
    return web3

def get_owner_keys():
    if web3.eth.get_balance(owner_address) <= web3.to_wei(1, "ether"):
        web3.eth.send_transaction({"from": web3.eth.accounts[0], "to": owner_address,
                                    "value": web3.to_wei(10, "ether"), "gasPrice": 1})
    return owner_address, owner_private_key

class Configuration:
    SQLALCHEMY_DATABASE_URI   = f"mysql+pymysql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_URL}:{DATABASE_PORT}/{DATABASE_NAME}" 
    JWT_SECRET_KEY            = JWT_SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES  = timedelta(hours = 1)
