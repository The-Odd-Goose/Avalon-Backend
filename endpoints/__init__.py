from flask import Flask
from endpoints.config import Config

def create_app(config_class=Config):

    # standard setup
    # more configuration within 
    app = Flask(__name__)
    app.config.from_object(Config)

    # here we'll have all the different routes required
    # it'll be from endpoints import blueprint
    # app.register_blueprint(blueprint)
    from endpoints.start import start

    app.register_blueprint(start)

    return app