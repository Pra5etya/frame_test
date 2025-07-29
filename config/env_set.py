import os
from config.data import get_database_uri


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY")

    # SQLALCHEMY_DATABASE_URI = get_database_uri()
    # SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    ENV = "development"


class StagingConfig(BaseConfig):
    DEBUG = True
    ENV = "staging"


class ProductionConfig(BaseConfig):
    DEBUG = False
    ENV = "production"