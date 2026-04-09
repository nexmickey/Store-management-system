from flask_sqlalchemy import SQLAlchemy

MAX_FIELD_LENGTH = 256
MIN_PASSWORD_LENGTH = 8

database = SQLAlchemy()

class User(database.Model):
    id       = database.Column(database.Integer, primary_key = True)
    email    = database.Column(database.String(MAX_FIELD_LENGTH), nullable = False, unique = True)
    password = database.Column(database.String(MAX_FIELD_LENGTH), nullable = False)
    forename = database.Column(database.String(MAX_FIELD_LENGTH), nullable = False)
    surname  = database.Column(database.String(MAX_FIELD_LENGTH), nullable = False)
    role_id  = database.Column(database.Integer, database.ForeignKey("role.id"), nullable = False)

    role = database.relationship("Role", backref="users") # reference to Role object

    def __repr__(self):
        return f"[User {self.id}, {self.email}, {self.role.name}]"

CUSTOMER = "customer"
COURIER  = "courier"
OWNER    = "owner"

class Role(database.Model):
    id   = database.Column(database.Integer, primary_key = True)
    name = database.Column(database.String(MAX_FIELD_LENGTH), nullable = False, unique = True)
    # self.users (relationship backref) reference to User objects

    def __repr__(self):
        return f"[Role {self.id}, {self.name}]"
