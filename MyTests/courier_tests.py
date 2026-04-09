import requests
from common import print_response, courier_url, headers, login, courier_data

def orders_to_deliver():
    print("Orders to deliver:")
    print_response(requests.get(courier_url + "/orders_to_deliver", headers=headers))

def pick_up_order():
    print("Pick up order:")
    data = {"id": 1}
    print_response(requests.post(courier_url + "/pick_up_order", headers=headers, json=data))

if (__name__ == "__main__"):
    login(courier_data)

    #orders_to_deliver()
    pick_up_order()
