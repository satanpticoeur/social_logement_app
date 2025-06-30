from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv() # Charge les variables d'environnement depuis .flaskenv

db = SQLAlchemy()
migrate = Migrate()
cors = CORS()

def create_app(config_class=None):
    app = Flask(__name__)

    if config_class is None:
        app.config.from_object('app.config.Config')
    else:
        app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})

    from app import models, routes

    app.register_blueprint(routes.api_bp, url_prefix='/api')
    return app