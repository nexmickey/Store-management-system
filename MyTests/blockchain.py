import requests
from common import  owner_url, print_response

def send_eth_to_owner():
    print("Eth transfer to owner:")
    print_response(requests.post(owner_url + "/transfer_eth_to_owner"))

def get_owner_eth():
    print("Get owner ETH balance:")
    print_response(requests.get(owner_url + "/get_owner_eth"))

if (__name__ == "__main__"):
    send_eth_to_owner()
    get_owner_eth()
