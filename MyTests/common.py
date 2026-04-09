import json
import requests

auth_url = "http://127.0.0.1:5000"
owner_url = "http://127.0.0.1:5001"
customer_url = "http://127.0.0.1:5002"
courier_url = "http://127.0.0.1:5003"

headers = {}

courier_data = {
    "email": "john@gmail.com",
    "password": "aA123456"
}
customer_data = {
    "email": "jane@gmail.com",
    "password": "aA123456"
}
owner_data = {
    "email": "onlymoney@gmail.com",
    "password": "evenmoremoney"
}

def print_response(response):
    print(f"Status code: {response.status_code}")
    try:
        data = response.json()
        print(f"Response JSON:\n{json.dumps(data, indent=2, sort_keys=True)}")
    except ValueError:
        if response.text: 
            print(f"Response text: {response.text}")
        else:
            print("Response body is empty.")
    print()

def login(user_data):
    response = requests.post(auth_url + "/login", json=user_data)
    # print(response.json()['accessToken'])
    headers["Authorization"] = f"Bearer {response.json()['accessToken']}"
    return response


def check_auth_alive():
    print("Check auth alive:")
    print_response(requests.get(auth_url + "/check_alive"))
def check_auth_alive_with_token():
    print("Check auth alive with token:")
    login(owner_data)
    print_response(requests.get(auth_url + "/check_token", headers=headers))
def check_owner_alive():
    print("Check owner alive:")
    print_response(requests.get(owner_url + "/check_alive"))

def get_all_users():
    print("Get all users:")
    print_response(requests.get(auth_url + "/get_all_users"))
def get_user(user_id = 1):
    print(f"Get user {user_id}:")
    print_response(requests.get(auth_url + f"/get_user/{user_id}"))
def get_all_roles():
    print("Get all roles:")
    print_response(requests.get(auth_url + "/get_all_roles"))
def all_products():
    print("All products:")
    print_response(requests.get(owner_url + "/all_products"))
def all_categories():
    print("All categories:")
    print_response(requests.get(owner_url + "/all_categories"))
def all_orders():
    print("All orders:")
    print_response(requests.get(owner_url + "/all_orders"))

if ( __name__ == "__main__" ):
    #check_auth_alive()
    #check_owner_alive()
    #get_user()
    #get_all_users()
    #get_all_roles()
    #login(owner_data)
    all_products()
    