import requests

from common import print_response, auth_url

user1 = {
    "forename": "Lazar",
    "surname": "Lazic",
    "email": "laza@example.com",
    "password": "laza1234"
}
user2 = {
    "forename": "Marko",
    "surname": "Markovic",
    "email": "marko@example.com",
    "password": "marko1234"
}

def register_customer():
    print("Register customer:")
    data = {
        "forename": user1["forename"],
        "surname": user1["surname"],
        "email": user1["email"],
        "password": user1["password"]
    }
    print_response(requests.post(auth_url + "/register_customer", json=data))

def register_courier():
    print("Register courier:")
    data = {
        "forename": user2["forename"],
        "surname": user2["surname"],
        "email": user2["email"],
        "password": user2["password"]
    }
    print_response(requests.post(auth_url + "/register_courier", json=data))

def register_missing_field_forename():
    print("Register missing field forename:")
    data = { }
    print_response(requests.post(auth_url + "/register_customer", json=data))

def register_missing_field_surname():
    print("Register missing field surname:")
    data = {
        "forename": user1["forename"]
    }
    print_response(requests.post(auth_url + "/register_customer", json=data))

def register_missing_field_email():
    print("Register missing field email:")
    data = {
        "forename": user1["forename"],
        "surname": user1["surname"]
    }
    print_response(requests.post(auth_url + "/register_customer", json=data))

def register_missing_field_password():
    print("Register missing field password:")
    data = {
        "forename": user1["forename"],
        "surname": user1["surname"],
        "email": user1["email"]
    }
    print_response(requests.post(auth_url + "/register_customer", json=data))

def register_invalid_email():
    print("Register invalid email:")
    data = {
        "forename": user1["forename"],
        "surname": user1["surname"],
        "email": "dsfsdf",
        "password": user1["password"]
    }
    print_response(requests.post(auth_url + "/register_customer", json=data))

def register_short_password():
    print("Register short password:")
    data = {
        "forename": user1["forename"],
        "surname": user1["surname"],
        "email": user1["email"],
        "password": "asd"
    }
    print_response(requests.post(auth_url + "/register_customer", json=data))

def register_too_long_forename():
    print("Register too long forename:")
    data = {
        "forename": "a" * 300,
        "surname": user1["surname"],
        "email": "asdasd@sdgsdf.com",
        "password": user1["password"]
    }
    print_response(requests.post(auth_url + "/register_customer", json=data))

def register_user_with_same_email_already_exists():
    print("Register user with same email already exists:")
    data = {
        "forename": user1["forename"],
        "surname": user1["surname"],
        "email": user1["email"],
        "password": user1["password"]
    }
    print_response(requests.post(auth_url + "/register_customer", json=data))


if ( __name__ == "__main__" ):
    register_customer()
    register_courier()
    register_missing_field_password()
    register_missing_field_email()
    register_missing_field_surname()
    register_missing_field_forename()
    register_invalid_email()
    register_short_password()
    # register_too_long_forename()
    register_user_with_same_email_already_exists()
