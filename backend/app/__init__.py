# backend/app/__init__.py
import json

from dotenv import load_dotenv
from flask import Flask, jsonify  # <-- Importez jsonify directement de flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
jwt = JWTManager()


# Pas besoin de la variable globale `cors = CORS()` si vous l'initialisez dans create_app.

def create_app(config_class=None):
    app = Flask(__name__)

    if config_class is None:
        app.config.from_object('app.config.Config')
    else:
        app.config.from_object(config_class)

    # Configuration JWT pour les cookies
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
    app.config["JWT_ACCESS_COOKIE_PATH"] = "/"

    # === MODIFICATIONS CRUCIALES POUR SAME_SITE ===
    # Pour le développement (HTTP), nous devons définir SameSite à 'Lax'
    # et JWT_COOKIE_SECURE à False.
    # Si vous passez en production (HTTPS), vous devrez mettre JWT_COOKIE_SECURE à True
    # et JWT_ACCESS_COOKIE_SAMESITE à 'None'.

    app.config["JWT_COOKIE_SECURE"] = False  # Important pour HTTP en dev
    app.config[
        "JWT_ACCESS_COOKIE_SAMESITE"] = "Lax"  # Par défaut, mais spécifions-le. Le navigateur le change en "None" si Secure=True
    # ^^^^^ Si 'Lax' ne suffit pas à cause de localhost/127.0.1, vous devrez passer à 'None'
    # mais ALORS vous devrez lancer votre backend en HTTPS (ex: via un proxy comme ngrok)
    # ou temporairement utiliser Flask-Env.

    app.config["JWT_COOKIE_CSRF_PROTECT"] = True  # Laissez à True pour la sécurité CSRF
    app.config["JWT_SECRET_KEY"] = "your_jwt_secret_key"

    db.init_app(app)
    migrate.init_app(app, db)

    # Configure CORS - Assurez-vous que l'URL de votre frontend est EXACTE.
    # Si votre frontend est sur http://localhost:5173, mettez 'http://localhost:5173'
    # Sinon, mettez '*' UNIQUEMENT POUR LE DÉVELOPPEMENT.
    CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173", "supports_credentials": True}})

    bcrypt.init_app(app)
    jwt.init_app(app)

    with app.app_context():
        from app import models, routes
        app.register_blueprint(routes.api_bp, url_prefix='/api')
        db.create_all()

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        json_identity_string = jwt_data["sub"]
        identity_data = json.loads(json_identity_string)  # Dé-sérialiser la string JSON en dict
        # Utilisez l'ID du dictionnaire dé-sérialisé
        return models.Utilisateur.query.filter_by(id=identity_data["id"]).first()

    @jwt.invalid_token_loader
    def invalid_token_callback(callback):
        return jsonify({"message": "Signature du token invalide."}), 401

    @jwt.unauthorized_loader
    def unauthorized_callback(callback):
        return jsonify({"message": "Requête non authentifiée. Veuillez vous connecter."}), 401

    return app
