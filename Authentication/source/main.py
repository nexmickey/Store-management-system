import time
import os

from flask import Flask, make_response, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_migrate import Migrate, init, migrate, upgrade
from sqlalchemy import and_, text
from helper import helper_bp
from datetime import timedelta

from configuration import FLASK_DEBUG, IS_DOCKER, Configuration
from models import database, User, Role, CUSTOMER, COURIER, OWNER, MAX_FIELD_LENGTH, MIN_PASSWORD_LENGTH
import re

email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"

application = Flask(__name__)
application.config.from_object(Configuration)
database.init_app(application)
migrate_ee = Migrate(application, database)

jwt = JWTManager(application)
application.register_blueprint(helper_bp)


def error_response(message, status_code = 400):
    return jsonify({"message": message}), status_code

def check_mandatory_fields(fields):
    for field in fields:
        if len(request.json.get(field, "")) == 0: 
            return error_response(f"Field {field} is missing.", 400)
    return None

def check_email(email):
    if re.match(email_pattern, email) is None:
        return False
    return True

def check_password(password):
    if len(password) < MIN_PASSWORD_LENGTH or len(password) > MAX_FIELD_LENGTH:
        return False
    return True

def check_any_field_has_max_length(fields):
    for field in fields:
        if len(request.json.get(field, "")) > MAX_FIELD_LENGTH:
            print (f"Field {field} is too long: {request.json.get(field, '')}", flush=True)


@application.route("/register_customer", methods=["POST"])
def register_customer():
    return register_new_user(CUSTOMER)
@application.route("/register_courier", methods=["POST"])
def register_courier():
    return register_new_user(COURIER)

register_fields = ["forename", "surname", "email", "password"]
def register_new_user(role_name):

    # check: missing fields, invalid email, password
    missing_fields_response = check_mandatory_fields(register_fields)
    if missing_fields_response is not None:
        return missing_fields_response
    
    if not check_email(request.json["email"]):
        return error_response("Invalid email.")

    if not check_password(request.json["password"]):
        return error_response("Invalid password.")
        
    # check: already exists user with same email
    existing_user = User.query.filter(User.email == request.json["email"]).count() > 0
    if existing_user:
        return error_response("Email already exists.")
    
    # check: any field is too long
    check_any_field_has_max_length(register_fields)

    role_of_user = Role.query.filter(Role.name == role_name).first()
    new_user = User(
        forename = request.json["forename"], 
        surname = request.json["surname"], 
        email = request.json["email"], 
        password = request.json["password"], 
        role_id = role_of_user.id
    )
    database.session.add(new_user)
    database.session.commit()

    return make_response("", 200)

login_fields = ["email", "password"]
@application.route("/login", methods = ["POST"])
def login():
    # check: missing fields, invalid email
    missing_fields_response = check_mandatory_fields(login_fields)
    if missing_fields_response is not None:
        return missing_fields_response

    if not check_email(request.json["email"]):
        return error_response("Invalid email.")

    # check: invalid credentials
    user = User.query.filter(and_(User.email == request.json["email"], User.password == request.json["password"])).first()
    if not user:
        return error_response("Invalid credentials.")
    
    # check: any field is too long
    check_any_field_has_max_length(login_fields)
        
    role = Role.query.filter(Role.id == user.role_id).first()
    claims = {
        "forename": user.forename, 
        "surname": user.surname, 
        "roles": role.name
    }
    return jsonify(accessToken = create_access_token(identity = user.email, additional_claims = claims, expires_delta = timedelta(hours=1)))

@application.route("/delete", methods = ["POST"])
@jwt_required()
def delete_user():
    user_email = get_jwt_identity()

    check_user = User.query.filter(User.email == user_email).first()
    if check_user:
        try:
            database.session.delete(check_user)
            database.session.commit()
        except Exception as e:
            database.session.rollback()
            return error_response(f"Database error: {str(e)}", 400)
        
        return make_response("", 200)
    
    return error_response("Unknown user.")

def wait_for_db(max_retries=10):
    retries = 0
    while retries < max_retries:
        try:
            database.session.execute(text('SELECT 1'))
            print("[+] Database working!")
            return True
        except Exception:
            retries += 1
            print(f"[-] Database not ready. Tries {retries}/{max_retries}")
            time.sleep(2)
    
    raise Exception("Could not connect to the database.")

# Create all tables, add roles and default owner user
@application.cli.command("init-db")
def init_db():
    print("[+] Initializing database...")
    try:
        wait_for_db()

        #database.create_all()

        if not os.path.exists("migrations/env.py"):
            print("[*] Migrations folder missing. Initializing...")
            init()
            migrate(message="Initial migration")
            upgrade()
        else:
            print("[*] Migrations folder found. Upgrading schema...")
            upgrade()

        roles = [CUSTOMER, COURIER, OWNER]
        for role_name in roles:
            if not Role.query.filter_by(name=role_name).first():
                database.session.add(Role(name=role_name))
        database.session.commit()

        owner_role = Role.query.filter(Role.name == OWNER).first()
        check_McDuck_already_exists = User.query.filter(User.email == "onlymoney@gmail.com").first()
        if check_McDuck_already_exists is None:
            new_user = User(
                forename = "Scrooge", 
                surname = "McDuck", 
                email = "onlymoney@gmail.com", 
                password = "evenmoremoney", 
                role_id = owner_role.id
            )
            database.session.add(new_user)
            
        database.session.commit()
        print("[+] Database initialized successfully!")
        
    except Exception as error:
        print(f"[-] Failed to initialize database: {error}")


if (__name__ == "__main__"):
    host_adr = "0.0.0.0" if IS_DOCKER else "127.0.0.1"
    application.run(host = host_adr, debug = FLASK_DEBUG, port = 5000)
