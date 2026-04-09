import requests
from common import print_response, customer_url, login, headers, customer_data

data_array = [
    {
        "requests": [
            {"id": 1, "quantity": 1},
            {"id": 2, "quantity": 1},
            {"id": 8, "quantity": 1}
        ]
    },
    {
        "requests123": [
            {"id": 1, "quantity": 1}
        ]
    },
    {
        "requests": [
            {"id": 2, "quantity": 1},
            {"quantity": 1},
        ]
    },
    {
        "requests": [
            {"id": 2, "quantity": 1},
            {"id": 1},
        ]
    },
    {
        "requests": [
            {"id": "x", "quantity": 1},
        ]
    },
    {
        "requests": [
            {"id": -1, "quantity": 1},
        ]
    },
    {
        "requests": [
            {"id": 2, "quantity": "x"},
        ]
    },
    {
        "requests": [
            {"id": 2, "quantity": -1},
        ]
    },
    {
        "requests": [
            {"id": 43534532, "quantity": 1},
        ]
    }
]

tests = [ 
    "[+] Order:",
    "[+] Order missing requests:",
    "[+] Order missing id:",
    "[+] Order missing quantity:",
    "[+] Order with invalid id 1:",
    "[+] Order with invalid id 2:",
    "[+] Order with invalid quantity 1:",
    "[+] Order with invalid quantity 2:",
    "[+] Order with non existing product:"
    "[+] Order with blockchain:"
]

def get_status():
    print("Status:")
    print_response(requests.get(customer_url + "/status", headers=headers))

def delivered():
    print("Delivered:")
    data = {"id": 2}
    print_response(requests.post(customer_url + "/delivered", headers=headers, json=data))

def customer_search():
    print("search:")
    params = {
        'name': '',
        'category': '0'
    }
    print_response(requests.get(customer_url + "/search", params=params))

if (__name__ == "__main__"):
    login(customer_data)

    """
    for index, data in enumerate(data_array):
        print(tests[index])
        print_response(requests.post(customer_url + "/order", json=data, headers=headers))
    """
    #get_status()
    delivered()
    #customer_search()
