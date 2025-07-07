from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, set_access_cookies, unset_jwt_cookies, jwt_required, get_jwt_identity
from app.models import Utilisateur
from app import db, bcrypt
import json

from datetime import timedelta
# Création du Blueprint pour les routes d'authentification
auth_bp = Blueprint('auth_bp', __name__, url_prefix='/api')



# Route d'inscription
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    nom_utilisateur = data.get('nom_utilisateur')
    email = data.get('email')
    mot_de_passe = data.get('mot_de_passe')
    telephone = data.get('telephone', None)
    cni = data.get('cni', None)
    role = data.get('role', 'locataire')  # Rôle par défaut 'locataire' si non spécifié

    if not nom_utilisateur or not email or not mot_de_passe or not role:
        return jsonify({"message": "Nom d'utilisateur, email, mot de passe et rôle sont requis."}), 400

    if Utilisateur.query.filter_by(nom_utilisateur=nom_utilisateur).first():
        return jsonify({"message": "Ce nom d'utilisateur existe déjà."}), 409
    if Utilisateur.query.filter_by(email=email).first():
        return jsonify({"message": "Cet email est déjà enregistré."}), 409
    if cni and Utilisateur.query.filter_by(cni=cni).first():
        return jsonify({"message": "Cette CNI est déjà enregistrée."}), 409

    new_user = Utilisateur(nom_utilisateur=nom_utilisateur, email=email, telephone=telephone, cni=cni, role=role)
    new_user.set_password(mot_de_passe)  # Hache le mot de passe

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify(
            {"message": "Utilisateur enregistré avec succès.", "user_id": new_user.id, "role": new_user.role}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Erreur lors de l'enregistrement: {str(e)}"}), 500


# Route de connexion
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    mot_de_passe = data.get('mot_de_passe')

    print(f"DEBUG: [LOGIN] Request received for email: {email}")
    if not email or not mot_de_passe:
        print("DEBUG: [LOGIN] Missing email or password. Returning 400.")
        return jsonify({"message": "Email et mot de passe sont requis."}), 400

    user = Utilisateur.query.filter_by(email=email).first()
    print(f"DEBUG: [LOGIN] User found: {user is not None}")

    if not user:
        print(f"DEBUG: [LOGIN] User not found for email: {email}. Returning 401.")
        return jsonify({"message": "Email ou mot de passe incorrect."}), 401

    if not user.check_password(mot_de_passe):
        print(f"DEBUG: [LOGIN] Password mismatch for user: {email}. Returning 401.")
        return jsonify({"message": "Email ou mot de passe incorrect."}), 401

    print(f"DEBUG: [LOGIN] User {email} authenticated successfully. Proceeding to token generation.")

    # >>> LA MODIFICATION CRUCIALE EST ICI <<<
    # Sérialisez l'identité en JSON string avant de la passer à create_access_token
    user_identity_data = {"id": user.id, "role": user.role, "email": user.email,
                          "nom_utilisateur": user.nom_utilisateur}
    json_identity_string = json.dumps(user_identity_data)  # Convertit le dict en string JSON

    try:
        access_token = create_access_token(
            identity=json_identity_string,  # Passe la string JSON comme identité
            expires_delta=timedelta(hours=24)
        )
        print(f"DEBUG: [LOGIN] Access Token generated (first 30 chars): {access_token[:30]}...")
    except Exception as e:
        print(f"ERROR: [LOGIN] Failed to create access token: {e}")
        return jsonify({"message": "Internal server error during token creation."}), 500

    response_data = {
        "message": "Connexion réussie.",
        "nom_utilisateur": user.nom_utilisateur,
        "role": user.role,
        "user_id": user.id,
        "email": user.email
    }

    response = jsonify(response_data)
    print(f"DEBUG: [LOGIN] Flask response object created.")

    try:
        set_access_cookies(response, access_token)
        print(f"DEBUG: [LOGIN] set_access_cookies called successfully.")

        # Vérification des headers pour débogage
        print(f"DEBUG: [LOGIN] Response headers after set_access_cookies: {response.headers}")
        if 'Set-Cookie' in str(response.headers):
            print("DEBUG: [LOGIN] 'Set-Cookie' header IS present in response object.")
        else:
            print("WARNING: [LOGIN] 'Set-Cookie' header IS NOT present in response object after set_access_cookies.")

    except Exception as e:
        print(f"ERROR: [LOGIN] Failed to set access cookies: {e}")
        return jsonify({"message": "Internal server error during cookie setting."}), 500

    print(f"DEBUG: [LOGIN] Returning response with status 200.")
    return response, 200


# Nouvelle route de déconnexion
@auth_bp.route('/logout', methods=['POST'])
def logout():
    response = jsonify({"message": "Déconnexion réussie."})
    unset_jwt_cookies(response)  # Supprime le cookie du token
    return response, 200


# backend/app/routes.py
@auth_bp.route('/protected', methods=['GET'])  # Assurez-vous que c'est bien GET si c'est pour checkAuthStatus
@jwt_required()
def protected_get_route():
    json_identity_string = get_jwt_identity()
    current_user_data = json.loads(json_identity_string)
    # Assurez-vous que vous retournez les informations user_id, role, email ici
    return jsonify(logged_in_as=current_user_data['id'], nom_utilisateur=current_user_data['nom_utilisateur'], role=current_user_data['role'],
                   email=current_user_data['email']), 200
