from datetime import timedelta
import os

DATABASE_URL        = os.environ.get("DATABASE_URL", "localhost")
DATABASE_USERNAME   = os.environ.get("DATABASE_USERNAME", "root")
DATABASE_PASSWORD   = os.environ.get("DATABASE_PASSWORD", "root")
DATABASE_NAME       = os.environ.get("DATABASE_NAME", "users")
DATABASE_PORT       = os.environ.get("DATABASE_PORT", "3306")
FLASK_DEBUG         = os.environ.get("FLASK_DEBUG", "true").lower() == "true"
JWT_SECRET_KEY      = os.environ.get("JWT_SECRET_KEY", "JWT_SECRET_DEV_KEY")
IS_DOCKER           = os.environ.get("IS_DOCKER", "false").lower() == "true"

class Configuration:
    SQLALCHEMY_DATABASE_URI   = f"mysql+pymysql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_URL}:{DATABASE_PORT}/{DATABASE_NAME}" 
    JWT_SECRET_KEY            = JWT_SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES  = timedelta(hours = 1)
    