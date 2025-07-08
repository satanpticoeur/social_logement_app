# backend/app/__init__.py
import json

from dotenv import load_dotenv
from flask import Flask, jsonify  # <-- Importez jsonify directement de flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

import os

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
jwt = JWTManager()


def create_app(config_class=None):
    app = Flask(__name__)

    UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

    # Extensions de fichiers autorisées
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS

    if config_class is None:
        app.config.from_object('app.config.Config')
    else:
        app.config.from_object(config_class)

    # Configuration JWT pour les cookies
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
    app.config["JWT_ACCESS_COOKIE_PATH"] = "/"


    app.config["JWT_COOKIE_SECURE"] = False
    app.config[
        "JWT_ACCESS_COOKIE_SAMESITE"] = "Lax"

    app.config["JWT_COOKIE_CSRF_PROTECT"] = True
    app.config["JWT_SECRET_KEY"] = "my_jwt_secret_key"

    db.init_app(app)
    migrate.init_app(app, db)

    CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173", "supports_credentials": True}})

    bcrypt.init_app(app)
    jwt.init_app(app)

    with app.app_context():
        from app import models
        from app.routes import auth_routes, user_routes, maison_routes, chambre_routes, contrat_routes, paiement_routes, rendez_vous_routes, media_routes, locataire_routes, proprietaire_routes, common_routes

        app.register_blueprint(auth_routes.auth_bp)
        app.register_blueprint(user_routes.user_bp)
        app.register_blueprint(maison_routes.maison_bp)
        app.register_blueprint(chambre_routes.chambre_bp)
        app.register_blueprint(contrat_routes.contrat_bp)
        app.register_blueprint(paiement_routes.paiement_bp)
        app.register_blueprint(rendez_vous_routes.rendez_vous_bp)
        app.register_blueprint(media_routes.media_bp)
        app.register_blueprint(locataire_routes.locataire_bp)
        app.register_blueprint(proprietaire_routes.proprietaire_bp)
        # app.register_blueprint(common_routes.common_bp)


        db.create_all()

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        json_identity_string = jwt_data["sub"]
        identity_data = json.loads(json_identity_string)
        return models.Utilisateur.query.filter_by(id=identity_data["id"]).first()

    @jwt.invalid_token_loader
    def invalid_token_callback(callback):

        return jsonify({"message": "Signature du token invalide."}), 401

    @jwt.unauthorized_loader
    def unauthorized_callback(callback):
        return jsonify({"message": "Requête non authentifiée. Veuillez vous connecter."}), 401

    return app
