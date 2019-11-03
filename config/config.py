class Config(object):
    DEBUG = False
    TESTING = False
    DATABASE_URI = 'mongodb://127.0.0.1:27017/chat'


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True