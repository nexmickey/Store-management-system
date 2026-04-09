import json
import secrets
from eth_account import Account
from web3 import Web3

filename = "owner_keys.json"
password = "my_very_cool_password"

def create_keystore_from_password():
    w3 = Web3() # HTTPProvider("http://127.0.0.1:8545")
    private_key = "0xb64be88dd6b89facf295f4fd0dda082efcbe95a2bb4478f5ee582b7efe88cf60"
    keystore_json = w3.eth.account.encrypt(private_key, password)

    with open(filename, 'w') as f:
        json.dump(keystore_json, f, indent=4)

    print(f"KeyStore file '{filename}' has been created.", flush=True)

def create_keystore():
    private_key = "0x" + secrets.token_hex(32)
    account     = Account.from_key(private_key)
    keystore    = account.encrypt(password)

    with open(filename, "w") as f:
        json.dump(keystore, f, indent=4)

    print(f"KeyStore file '{filename}' has been created.", flush=True)

def create_account():
    web3        = Web3()
    private_key = "0x" + secrets.token_hex(32)
    account     = Account.from_key(private_key)
    address     = account.address
    _ = web3.eth.send_transaction ({
        "from": web3.eth.accounts[0],
        "to": address,
        "value": web3.to_wei(2, "ether"),
        "gasPrice": 1
    })
    return (address, private_key)

if (__name__ == "__main__"):
    create_keystore_from_password()
    # create_keystore()
    # create_account()
