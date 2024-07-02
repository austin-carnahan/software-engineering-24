import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'mysecret')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'myjwtsecret')
    MONGODB_SETTINGS = {
        'db': 'budget_db',
        'host': 'localhost',
        'port': 27017
    }

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    DATABASE_URI = 'sqlite:///dev.db'

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DATABASE_URI = 'sqlite:///:memory:'

class ProductionConfig(Config):
    """Production configuration."""
    DATABASE_URI = 'sqlite:///prod.db'