import requests
from common import print_response, owner_url, login, headers, owner_data

def update():
    print("Update:")
    files = {"file": open("data/update.csv", "rb")}
    print_response(requests.post(owner_url + "/update", headers=headers, files=files))

def missing_file():
    print("Missing file:")
    print_response(requests.post(owner_url + "/update", headers=headers))

def empty_file():
    print("Empty file:")
    files = {"file": open("data/empty.csv", "rb")}
    print_response(requests.post(owner_url + "/update", headers=headers, files=files))

def wrong_row_length():
    print("Wrong row length:")
    files = {"file": open("data/wrong_row_length.csv", "rb")}
    print_response(requests.post(owner_url + "/update", headers=headers, files=files))

def wrong_price_1():
    print("Wrong price 1:")
    files = {"file": open("data/wrong_price_1.csv", "rb")}
    print_response(requests.post(owner_url + "/update", headers=headers, files=files))

def wrong_price_2():
    print("Wrong price 2:")
    files = {"file": open("data/wrong_price_2.csv", "rb")}
    print_response(requests.post(owner_url + "/update", headers=headers, files=files))

def empty_field():
    print("Empty field:")
    files = {"file": open("data/empty_field.csv", "rb")}
    print_response(requests.post(owner_url + "/update", headers=headers, files=files))

if ( __name__ == "__main__" ):
    login(owner_data)

    update()
    missing_file()
    empty_file()
    wrong_row_length()
    wrong_price_1()
    wrong_price_2()
    empty_field()
