import requests
from common import auth_url, owner_url

def print_response(response):
    print(f"Status code: {response.status_code}")
    print(f"Response text: {response.text}\n")

if ( __name__ == "__main__" ):
    print("Delete auth:")
    print_response(requests.delete(auth_url + "/delete_data"))
    print("Delete shop:")
    print_response(requests.delete(owner_url + "/delete_data"))
    