
from flask import Flask
from flask_migrate import Migrate
from models import database
from configuration import Configuration

def create_app():
    app = Flask(__name__)
    app.config.from_object(Configuration)
    database.init_app(app)
    from models import User, Role
    Migrate(app, database)
    return app

application = create_app()