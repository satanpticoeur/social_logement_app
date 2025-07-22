# backend/app/routes/auth_routes.py

from flask import jsonify, request, redirect, current_app
from flask_jwt_extended import create_access_token, set_access_cookies, unset_jwt_cookies, jwt_required, get_jwt_identity
from flask_restx import Namespace, Resource, fields # <--- NOUVEAUX IMPORTS
from app.models import Utilisateur
from app import db, bcrypt # Assurez-vous que db et bcrypt sont bien importés depuis app
import json
from datetime import timedelta

# --- Définir un Namespace pour les routes d'authentification ---
# Ce Namespace sera ajouté à l'objet 'api' global dans __init__.py
ns_auth = Namespace('auth', description='Opérations liées à l\'authentification et la gestion des utilisateurs')

# --- Modèles de Données pour Swagger (pour documenter les requêtes/réponses) ---

# Modèle pour la requête d'inscription
register_request_model = ns_auth.model('RegisterRequest', {
    'nom_utilisateur': fields.String(required=True, description='Nom d\'utilisateur unique'),
    'email': fields.String(required=True, description='Adresse email unique'),
    'mot_de_passe': fields.String(required=True, description='Mot de passe (min. 6 caractères)', min_length=6),
    'telephone': fields.String(description='Numéro de téléphone (optionnel)'),
    'cni': fields.String(description='Numéro de Carte Nationale d\'Identité (optionnel)'),
    'role': fields.String(description='Rôle de l\'utilisateur (locataire, proprietaire, admin)', enum=['locataire', 'proprietaire', 'admin'], default='locataire')
})

# Modèle pour la réponse d'inscription réussie
register_success_response_model = ns_auth.model('RegisterSuccess', {
    'message': fields.String(description='Message de succès'),
    'user_id': fields.Integer(description='ID de l\'utilisateur créé'),
    'role': fields.String(description='Rôle de l\'utilisateur')
})

# Modèle pour la requête de connexion
login_request_model = ns_auth.model('LoginRequest', {
    'email': fields.String(required=True, description='Adresse email de l\'utilisateur'),
    'mot_de_passe': fields.String(required=True, description='Mot de passe de l\'utilisateur')
})

# Modèle pour la réponse de connexion réussie
login_success_response_model = ns_auth.model('LoginSuccess', {
    'message': fields.String(description='Message de succès'),
    'nom_utilisateur': fields.String(description='Nom d\'utilisateur'),
    'role': fields.String(description='Rôle de l\'utilisateur'),
    'user_id': fields.Integer(description='ID de l\'utilisateur'),
    'email': fields.String(description='Email de l\'utilisateur')
})

# Modèle pour la réponse de déconnexion
logout_response_model = ns_auth.model('LogoutSuccess', {
    'message': fields.String(description='Message de déconnexion')
})

# Modèle pour la réponse de la route protégée (vérification de statut d'auth)
protected_response_model = ns_auth.model('ProtectedResponse', {
    'logged_in_as': fields.Integer(description='ID de l\'utilisateur connecté'),
    'nom_utilisateur': fields.String(description='Nom d\'utilisateur connecté'),
    'role': fields.String(description='Rôle de l\'utilisateur connecté'),
    'email': fields.String(description='Email de l\'utilisateur connecté')
})


@ns_auth.route('/register')
class UserRegister(Resource):
    @ns_auth.expect(register_request_model, validate=True) # Spécifie le modèle de corps de requête
    @ns_auth.marshal_with(register_success_response_model, code=201) # Spécifie le modèle de réponse 201
    @ns_auth.response(400, 'Champs manquants ou invalides')
    @ns_auth.response(409, 'Nom d\'utilisateur, email ou CNI déjà utilisé')
    @ns_auth.response(500, 'Erreur interne du serveur')
    def post(self):
        """
        Enregistre un nouvel utilisateur.
        """
        # ns_auth.payload contient les données validées par @ns_auth.expect
        data = ns_auth.payload
        nom_utilisateur = data.get('nom_utilisateur')
        email = data.get('email')
        mot_de_passe = data.get('mot_de_passe')
        telephone = data.get('telephone')
        cni = data.get('cni')
        role = data.get('role', 'locataire')

        if Utilisateur.query.filter_by(nom_utilisateur=nom_utilisateur).first():
            ns_auth.abort(409, "Ce nom d'utilisateur existe déjà.")
        if Utilisateur.query.filter_by(email=email).first():
            ns_auth.abort(409, "Cet email est déjà enregistré.")
        if cni and Utilisateur.query.filter_by(cni=cni).first():
            ns_auth.abort(409, "Cette CNI est déjà enregistrée.")

        new_user = Utilisateur(nom_utilisateur=nom_utilisateur, email=email, telephone=telephone, cni=cni, role=role)
        new_user.set_password(mot_de_passe)

        try:
            db.session.add(new_user)
            db.session.commit()
            return {
                "message": "Utilisateur enregistré avec succès.",
                "user_id": new_user.id,
                "role": new_user.role
            }, 201
        except Exception as e:
            db.session.rollback()
            ns_auth.abort(500, f"Erreur lors de l'enregistrement: {str(e)}")


@ns_auth.route('/login')
class UserLogin(Resource):
    @ns_auth.expect(login_request_model, validate=True)
    # @ns_auth.marshal_with(login_success_response_model, code=200)
    @ns_auth.response(200, 'Connexion réussie', model=login_success_response_model)
    @ns_auth.response(400, 'Email et mot de passe requis')
    @ns_auth.response(401, 'Email ou mot de passe incorrect')
    @ns_auth.response(500, 'Erreur interne du serveur')
    def post(self):
        """
        Connecte un utilisateur et définit les cookies JWT.
        """
        data = ns_auth.payload
        email = data.get('email')
        mot_de_passe = data.get('mot_de_passe')

        user = Utilisateur.query.filter_by(email=email).first()

        if not user or not user.check_password(mot_de_passe):
            ns_auth.abort(401, "Email ou mot de passe incorrect.")

        user_identity_data = {"id": user.id, "role": user.role, "email": user.email,
                              "nom_utilisateur": user.nom_utilisateur}
        json_identity_string = json.dumps(user_identity_data)

        try:
            access_token = create_access_token(
                identity=json_identity_string,  # Passe la string JSON comme identité
                expires_delta=timedelta(hours=24)
            )
        except Exception as e:
            return jsonify({"message": "Internal server error during token creation."}), 500

        response_data = {
            "message": "Connexion réussie.",
            "nom_utilisateur": user.nom_utilisateur,
            "role": user.role,
            "user_id": user.id,
            "email": user.email
        }
        response = jsonify(response_data)
        response.status_code = 200
        try:
            set_access_cookies(response, access_token)
            if 'Set-Cookie' in str(response.headers):
                print("DEBUG: [LOGIN] 'Set-Cookie' header IS present in response object.")
            else:
                print("WARNING: [LOGIN] 'Set-Cookie' header IS NOT present in response object after set_access_cookies.")
        except Exception as e:
            print(f"ERROR: [LOGIN] Failed to set access cookies: {e}")
            return jsonify({"message": "Internal server error during cookie setting."}), 500

        return response

@ns_auth.route('/logout')
class UserLogout(Resource):
    @ns_auth.doc(security='apikey')
    @ns_auth.response(200, 'Déconnexion réussie', model=logout_response_model)
    def post(self):
        """
        Déconnecte l'utilisateur en supprimant les cookies JWT.
        """

        response = jsonify({"message": "Déconnexion réussie."})
        response.status_code = 200
        unset_jwt_cookies(response)
        return response


@ns_auth.route('/protected')
class ProtectedRoute(Resource):
    @jwt_required()
    @ns_auth.doc(security='apikey') # Indique que cette route nécessite un jeton JWT
    @ns_auth.marshal_with(protected_response_model)
    @ns_auth.response(200, 'Succès')
    @ns_auth.response(401, 'Non autorisé')
    def get(self):
        """
        Vérifie le statut d'authentification de l'utilisateur.
        """
        json_identity_string = get_jwt_identity()
        current_user_data = json.loads(json_identity_string)

        return {
            "logged_in_as": current_user_data['id'],
            "nom_utilisateur": current_user_data['nom_utilisateur'],
            "role": current_user_data['role'],
            "email": current_user_data['email']
        }, 200