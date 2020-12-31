from flask import Flask
from endpoints.config import Config
from flask_cors import CORS

def create_app(config_class=Config):

    # standard setup
    app = Flask(__name__)

    # cors setup
    cors = CORS(app, resources={r"/*": {"origins": ["https://the-odd-goose.web.app", "https://the-odd-goose.firebaseapp.com"]}})

    # more configuration within 
    app.config.from_object(Config)

    # here we'll have all the different routes required
    # it'll be from endpoints import blueprint
    # app.register_blueprint(blueprint)
    from endpoints.start import start
    from endpoints.turns import turns

    app.register_blueprint(start)
    app.register_blueprint(turns)

    return app