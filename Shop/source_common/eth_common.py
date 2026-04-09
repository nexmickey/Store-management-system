from flask import Blueprint, make_response

from .configuration import get_owner_keys, read_file, get_web3

helper_eth_bp = Blueprint("helper_eth", __name__)

def test_connection():
    return get_web3().is_connected()

def read_abi_bytecode():
    return read_file("../solidity/output/DeliveryContract.abi"), read_file("../solidity/output/DeliveryContract.bin")

def send_transaction(tx, private_key):
    web3 = get_web3()
    signed_tx = web3.eth.account.sign_transaction(tx, private_key)
    tx_hash   = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
    return web3.eth.wait_for_transaction_receipt(tx_hash)

def create_and_deploy_contract(customer_public_address, price):
    web3 = get_web3()
    owner_address, owner_key = get_owner_keys()
    abi, bytecode = read_abi_bytecode()

    try:
        new_contract = web3.eth.contract(abi = abi, bytecode = bytecode)
        tx = new_contract.constructor(customer_public_address, price).build_transaction({
            "from": owner_address,
            "gasPrice": web3.eth.gas_price,
            "nonce": web3.eth.get_transaction_count(owner_address)
        })
        tx["gas"] = web3.eth.estimate_gas(tx)

        receipt = send_transaction(tx, owner_key)
        print(f"Contract deployed at address: {receipt.contractAddress}", flush = True)
        return receipt.contractAddress
    except Exception as e:
        print(f"Error while deploying contract: {e}", flush = True)
    return None


@helper_eth_bp.route("/get_owner_eth", methods=["GET"])
def get_owner_eth():
    web3 = get_web3()
    owner_balance = str(web3.from_wei(web3.eth.get_balance(get_owner_keys()[0]), "ether"))
    zero_account_balance = str(web3.from_wei(web3.eth.get_balance(web3.eth.accounts[0]), "ether"))
    print(f"[+] Owner balance: {owner_balance} ether", flush = True)
    print(f"[+] Zero account balance: {zero_account_balance} ether", flush = True)

    return make_response({"owner balance": owner_balance + " ether", "zero account balance": zero_account_balance + " ether"}, 200)

@helper_eth_bp.route("/transfer_eth_to_owner", methods=["POST"])
def transfer_eth_to_owner():
    web3 = get_web3()
    tx_hash = web3.eth.send_transaction({
        "from": web3.eth.accounts[0],
        "to": get_owner_keys()[0],
        "value": web3.to_wei (10, "ether"),
        "gasPrice": 1
    })
    _ = web3.eth.wait_for_transaction_receipt(tx_hash)

    owner_address, _ = get_owner_keys()
    owner_balance = str(web3.from_wei(web3.eth.get_balance(owner_address), "ether"))
    zero_account_balance = str(web3.from_wei(web3.eth.get_balance(web3.eth.accounts[0]), "ether"))
    print(f"[+] Owner balance: {owner_balance} ether", flush = True)
    print(f"[+] Zero account balance: {zero_account_balance} ether", flush = True)

    return make_response("Successful transaction", 200)
