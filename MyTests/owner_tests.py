import requests

from common import print_response, owner_url, headers, login, owner_data

def product_statistics():
    print("Product statistics:")
    print_response(requests.get(owner_url + "/product_statistics", headers=headers))

def category_statistics():
    print("Category statistics:")
    print_response(requests.get(owner_url + "/category_statistics", headers=headers))

if (__name__ == "__main__"):
    login(owner_data)

    #product_statistics()
    category_statistics()