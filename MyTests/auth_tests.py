import requests

from common import print_response, auth_url, login, headers, courier_data, customer_data, owner_data

def delete_user():
    print("Delete user:")
    print_response(requests.post(auth_url + "/delete", headers=headers))

def delete_user_missing_auth():
    print("Delete user missing auth:")
    print_response(requests.post(auth_url + "/delete"))

if ( __name__ == "__main__" ):
    login(customer_data) # customer_data, owner_data

    delete_user()
    #delete_user_missing_auth()
    