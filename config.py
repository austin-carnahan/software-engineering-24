class Config:
    """Base configuration."""
    DEBUG = False
    TESTING = False
    DATABASE_URI = 'sqlite:///:memory:'

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