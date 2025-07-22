import json
import os

import paydunya
from dotenv import load_dotenv
from flask import Flask, jsonify, send_from_directory
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_restx import Api
from flask_sqlalchemy import SQLAlchemy

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

    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS

    if config_class is None:
        app.config.from_object('app.config.Config')
    else:
        app.config.from_object(config_class)

    # app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
    # app.config["JWT_ACCESS_COOKIE_PATH"] = "/"
    # app.config["JWT_COOKIE_SECURE"] = False
    # app.config["JWT_ACCESS_COOKIE_SAMESITE"] = "Lax"
    # app.config["JWT_COOKIE_CSRF_PROTECT"] = True
    # app.config['JWT_CSRF_HEADER_NAME'] = 'X-CSRF-TOKEN'

    app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    app.config['JWT_COOKIE_SECURE'] = False  # True en prod avec HTTPS
    app.config['JWT_COOKIE_CSRF_PROTECT'] = True
    app.config['JWT_CSRF_HEADER_NAME'] = 'X-CSRF-TOKEN'
    app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token_cookie'
    app.config['JWT_CSRF_IN_COOKIES'] = True
    app.config['JWT_ACCESS_COOKIE_PATH'] = '/'
    app.config["JWT_SECRET_KEY"] = os.environ.get('JWT_SECRET_KEY', 'my_jwt_secret_key_default_if_not_set')

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # Configuration CORS
    CORS(app, resources={r"/api/*": {"origins": "*", "supports_credentials": True}})

    # Configuration PayDunya
    PAYDUNYA_ACCESS_TOKENS = {
        'PAYDUNYA-MASTER-KEY': app.config['PAYDUNYA_MASTER_KEY'],
        'PAYDUNYA-PRIVATE-KEY': app.config['PAYDUNYA_PRIVATE_KEY'],
        'PAYDUNYA-TOKEN': app.config['PAYDUNYA_TOKEN'],
    }
    paydunya.debug = True
    paydunya.api_keys = PAYDUNYA_ACCESS_TOKENS

    # --- Initialisation de Flask-RESTx pour Swagger ---
    api = Api(app,
              version='1.0',
              title='Social Logement API',
              description='API pour la gestion des locations et paiements des locataires et propriétaires.',
              doc='/',
              prefix='/api',
              authorizations={
                  'csrfToken': {
                      'type': 'apiKey',
                      'in': 'header',
                      'name': 'X-CSRF-TOKEN',
                      'description': 'CSRF token à inclure dans les requêtes POST/PUT/DELETE',
                  }
              },
              security='csrfToken',
              swagger_ui_template='swagger-ui.html',  # Nom du template personnalisé
              swagger_ui_static_url='/api/swagger_static/'
              )

    # Vous devez servir un dossier statique pour vos fichiers Swagger personnalisés
    @app.route('/api/swagger_static/<path:filename>')
    def serve_swagger_custom_static(filename):
        return send_from_directory(os.path.join(app.root_path, 'static', 'swagger_custom'), filename)

    # ---------------------------------------------------

    with app.app_context():
        from app import models

        from app.routes.proprietaire_routes import proprietaire_ns
        from app.routes.auth_routes import ns_auth

        api.add_namespace(ns_auth, path='/auth')
        api.add_namespace(proprietaire_ns, path='/proprietaire')

        db.create_all()

    # Gestionnaires d'erreurs JWT
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
