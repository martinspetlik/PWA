import os
config = {
    "development": "config.DevelopmentConfig",
    "testing": "config.TestingConfig",
    "default": "config.DevelopmentConfig"
}


def configure_app(app):
    config_name = os.getenv('FLASK_CONFIGURATION', 'default')

    print("config name ", config_name)

    app.config.from_object(config[config_name]) # object-based default configuration
    #app.config.from_pyfile('config.cfg', silent=True) # instance-folders configuration