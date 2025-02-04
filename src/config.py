import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Environment variables for SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True

    # Environment variable for JWT secret key
    JWT_SECRET_KEY = os.environ.get("SECRET_KEY")
