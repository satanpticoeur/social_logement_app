import json
from datetime import datetime, date  # Assure-toi que datetime et date sont importés
from datetime import timedelta
from decimal import Decimal  # Assure-toi que Decimal est importé

from dateutil.relativedelta import relativedelta
from flask import Blueprint, jsonify, request, abort
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, set_access_cookies, \
    unset_jwt_cookies

from app import db
from app.models import Utilisateur, Maison, Chambre, Contrat, Paiement, RendezVous, Media

api_bp = Blueprint('api', __name__)


# Route d'inscription
@api_bp.route('/register', methods=['POST'])
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
@api_bp.route('/login', methods=['POST'])
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
    user_identity_data = {"id": user.id, "role": user.role, "email": user.email}
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


# ... (votre route logout) ...

# ... (votre route protected) ...
# IMPORTANT : Dans vos routes protégées, vous devrez dé-sérialiser l'identité :
# @api_bp.route('/protected', methods=['GET'])
# @jwt_required()
# def protected_get_route():
#     json_identity_string = get_jwt_identity()
#     current_user_data = json.loads(json_identity_string) # Dé-sérialiser la string JSON en dict
#     # Maintenant current_user_data est un dictionnaire, ex: current_user_data['id']
#     return jsonify(message=f"Ceci est une route protégée pour {current_user_data['email']}."), 200

# Nouvelle route de déconnexion
@api_bp.route('/logout', methods=['POST'])
def logout():
    response = jsonify({"message": "Déconnexion réussie."})
    unset_jwt_cookies(response)  # Supprime le cookie du token
    return response, 200


# backend/app/routes.py
@api_bp.route('/protected', methods=['GET']) # Assurez-vous que c'est bien GET si c'est pour checkAuthStatus
@jwt_required()
def protected_get_route():
    json_identity_string = get_jwt_identity()
    current_user_data = json.loads(json_identity_string)
    # Assurez-vous que vous retournez les informations user_id, role, email ici
    return jsonify(logged_in_as=current_user_data, user_id=current_user_data['id'], role=current_user_data['role'], email=current_user_data['email']), 200

# --- Fonctions utilitaires de sérialisation (améliorées et nouvelles) ---


def serialize_utilisateur(utilisateur):
    if not utilisateur:
        return None
    return {
        "id": utilisateur.id,
        "nom_utilisateur": utilisateur.nom_utilisateur,
        "email": utilisateur.email,
        "telephone": utilisateur.telephone,
        "cni": utilisateur.cni,
        "role": utilisateur.role,
        "cree_le": utilisateur.cree_le.isoformat() if utilisateur.cree_le else None,
    }


def serialize_maison(maison):
    if not maison:
        return None
    return {
        "id": maison.id,
        "proprietaire_id": maison.proprietaire_id,
        "adresse": maison.adresse,
        "latitude": str(maison.latitude) if maison.latitude is not None else None,  # Convertir Decimal en str
        "longitude": str(maison.longitude) if maison.longitude is not None else None,  # Convertir Decimal en str
        "description": maison.description,
        "cree_le": maison.cree_le.isoformat() if maison.cree_le else None,
        # Inclure le propriétaire si joint par joinedload
        "proprietaire": serialize_utilisateur(maison.proprietaire) if hasattr(maison, 'proprietaire') else None
    }


def serialize_media(media):
    if not media:
        return None
    return {
        "id": media.id,
        "chambre_id": media.chambre_id,
        "url": media.url,
        "type": media.type,
        "description": media.description,
        "cree_le": media.cree_le.isoformat() if media.cree_le else None,
    }


def serialize_chambre(chambre):
    if not chambre:
        return None
    return {
        "id": chambre.id,
        "maison_id": chambre.maison_id,
        "titre": chambre.titre,
        "description": chambre.description,
        "taille": chambre.taille,
        "type": chambre.type,
        "meublee": chambre.meublee,
        "salle_de_bain": chambre.salle_de_bain,
        "prix": str(chambre.prix) if chambre.prix is not None else None,  # Convertir Decimal en str
        "disponible": chambre.disponible,
        "cree_le": chambre.cree_le.isoformat() if chambre.cree_le else None,
        # Inclure la maison et les médias si joints
        "maison": serialize_maison(chambre.maison) if hasattr(chambre, 'maison') else None,
        "medias": [serialize_media(m) for m in chambre.medias] if hasattr(chambre, 'medias') and chambre.medias else []
    }


def serialize_contrat(contrat):
    if not contrat:
        return None
    return {
        "id": contrat.id,
        "locataire_id": contrat.locataire_id,
        "chambre_id": contrat.chambre_id,
        "date_debut": contrat.date_debut.isoformat() if contrat.date_debut else None,
        "date_fin": contrat.date_fin.isoformat() if contrat.date_fin else None,
        "montant_caution": str(contrat.montant_caution) if contrat.montant_caution is not None else None,
        # Convertir Decimal en str
        "mois_caution": contrat.mois_caution,
        "description": contrat.description,  # Nouveau champ
        "mode_paiement": contrat.mode_paiement,  # Nouveau champ
        "periodicite": contrat.periodicite,  # Nouveau champ
        "statut": contrat.statut,  # Nouveau champ
        "cree_le": contrat.cree_le.isoformat() if contrat.cree_le else None,
        # Inclure les relations chargées par joinedload
        "locataire": serialize_utilisateur(contrat.locataire) if hasattr(contrat, 'locataire') else None,
        "chambre": serialize_chambre(contrat.chambre) if hasattr(contrat, 'chambre') else None
    }


def serialize_paiement(paiement):
    if not paiement:
        return None
    return {
        "id": paiement.id,
        "contrat_id": paiement.contrat_id,
        "montant": str(paiement.montant) if paiement.montant is not None else None,  # Convertir Decimal en str
        "date_paiement": paiement.date_paiement.isoformat() if paiement.date_paiement else None,
        "statut": paiement.statut,
        "cree_le": paiement.cree_le.isoformat() if paiement.cree_le else None,
        # Inclure le contrat si joint par joinedload
        "contrat": serialize_contrat(paiement.contrat) if hasattr(paiement, 'contrat') else None
    }


def serialize_rendez_vous(rdv):
    if not rdv:
        return None
    return {
        "id": rdv.id,
        "locataire_id": rdv.locataire_id,
        "chambre_id": rdv.chambre_id,
        "date_heure": rdv.date_heure.isoformat() if rdv.date_heure else None,
        "statut": rdv.statut,
        "cree_le": rdv.cree_le.isoformat() if rdv.cree_le else None,
        "locataire": serialize_utilisateur(rdv.locataire) if hasattr(rdv, 'locataire') else None,
        "chambre": serialize_chambre(rdv.chambre) if hasattr(rdv, 'chambre') else None,
    }


def serialize_probleme(probleme):
    if not probleme:
        return None
    return {
        "id": probleme.id,
        "contrat_id": probleme.contrat_id,
        "signale_par": probleme.signale_par,
        "description": probleme.description,
        "type": probleme.type,
        "responsable": probleme.responsable,
        "resolu": probleme.resolu,
        "cree_le": probleme.cree_le.isoformat() if probleme.cree_le else None,
        "contrat": serialize_contrat(probleme.contrat) if hasattr(probleme, 'contrat') else None,
    }


# --- CRUD pour les Utilisateurs (restent les mêmes) ---

@api_bp.route('/utilisateurs', methods=['POST'])
def create_utilisateur():
    data = request.get_json()
    if not data or not all(k in data for k in ['email', 'role']):
        abort(400, description="Email et role sont requis.")

    if Utilisateur.query.filter_by(email=data['email']).first():
        abort(409, description="Un utilisateur avec cet email existe déjà.")

    new_utilisateur = Utilisateur(
        nom_utilisateur=data.get('nom_utilisateur'),
        email=data['email'],
        telephone=data.get('telephone'),
        cni=data.get('cni'),
        role=data['role']
    )
    db.session.add(new_utilisateur)
    db.session.commit()
    return jsonify(serialize_utilisateur(new_utilisateur)), 201


@api_bp.route('/utilisateurs', methods=['GET'])
def get_utilisateurs():
    # User Story 1 & 6: Filtrer par rôle (locataire) ou obtenir tous les utilisateurs
    role_filter = request.args.get('role')
    query = Utilisateur.query
    if role_filter:
        query = query.filter_by(role=role_filter)
    utilisateurs = query.all()
    return jsonify([serialize_utilisateur(u) for u in utilisateurs]), 200


@api_bp.route('/utilisateurs/<int:utilisateur_id>', methods=['GET'])
def get_utilisateur(utilisateur_id):
    utilisateur = Utilisateur.query.get_or_404(utilisateur_id)
    return jsonify(serialize_utilisateur(utilisateur)), 200


@api_bp.route('/utilisateurs/<int:utilisateur_id>', methods=['PUT'])
def update_utilisateur(utilisateur_id):
    utilisateur = Utilisateur.query.get_or_404(utilisateur_id)
    data = request.get_json()

    if not data:
        abort(400, description="Données de mise à jour requises.")

    utilisateur.nom_utilisateur = data.get('nom_utilisateur', utilisateur.nom_utilisateur)
    if 'email' in data:  # Permettre la mise à jour de l'email, mais vérifier l'unicité
        if Utilisateur.query.filter(Utilisateur.email == data['email'], Utilisateur.id != utilisateur_id).first():
            abort(409, description="Cet email est déjà utilisé par un autre utilisateur.")
        utilisateur.email = data['email']
    utilisateur.telephone = data.get('telephone', utilisateur.telephone)
    utilisateur.cni = data.get('cni', utilisateur.cni)
    utilisateur.role = data.get('role', utilisateur.role)

    try:
        db.session.commit()
        return jsonify(serialize_utilisateur(utilisateur)), 200
    except Exception as e:
        db.session.rollback()
        abort(500, description=f"Erreur lors de la mise à jour de l'utilisateur: {str(e)}")


@api_bp.route('/utilisateurs/<int:utilisateur_id>', methods=['DELETE'])
def delete_utilisateur(utilisateur_id):
    utilisateur = Utilisateur.query.get_or_404(utilisateur_id)
    db.session.delete(utilisateur)
    db.session.commit()
    return jsonify(message="Utilisateur supprimé avec succès"), 204


# --- CRUD pour les Maisons (restent les mêmes, mais la sérialisation est améliorée) ---

@api_bp.route('/maisons', methods=['POST'])
def create_maison():
    data = request.get_json()
    if not data or not all(k in data for k in ['proprietaire_id', 'adresse']):
        abort(400, description="proprietaire_id et adresse sont requis.")

    if not Utilisateur.query.get(data['proprietaire_id']):
        abort(404, description="Le propriétaire spécifié n'existe pas.")

    new_maison = Maison(
        proprietaire_id=data['proprietaire_id'],
        adresse=data['adresse'],
        latitude=data.get('latitude'),
        longitude=data.get('longitude'),
        description=data.get('description')
    )
    db.session.add(new_maison)
    db.session.commit()
    return jsonify(serialize_maison(new_maison)), 201


@api_bp.route('/maisons', methods=['GET'])
def get_maisons():
    maisons = Maison.query.all()
    return jsonify([serialize_maison(m) for m in maisons]), 200


@api_bp.route('/maisons/<int:maison_id>', methods=['GET'])
def get_maison(maison_id):
    # Charger la maison et son propriétaire pour la sérialisation
    maison = Maison.query.options(db.joinedload(Maison.proprietaire)).get_or_404(maison_id)
    return jsonify(serialize_maison(maison)), 200


@api_bp.route('/maisons/<int:maison_id>', methods=['PUT'])
def update_maison(maison_id):
    maison = Maison.query.get_or_404(maison_id)
    data = request.get_json()

    if not data:
        abort(400, description="Données de mise à jour requises.")

    maison.adresse = data.get('adresse', maison.adresse)
    maison.latitude = data.get('latitude', maison.latitude)
    maison.longitude = data.get('longitude', maison.longitude)
    maison.description = data.get('description', maison.description)

    if 'proprietaire_id' in data and data['proprietaire_id'] != maison.proprietaire_id:
        if not Utilisateur.query.get(data['proprietaire_id']):
            abort(404, description="Le nouveau propriétaire spécifié n'existe pas.")
        maison.proprietaire_id = data['proprietaire_id']

    try:
        db.session.commit()
        return jsonify(serialize_maison(maison)), 200
    except Exception as e:
        db.session.rollback()
        abort(500, description=f"Erreur lors de la mise à jour de la maison: {str(e)}")


@api_bp.route('/maisons/<int:maison_id>', methods=['DELETE'])
def delete_maison(maison_id):
    maison = Maison.query.get_or_404(maison_id)
    db.session.delete(maison)
    db.session.commit()
    return jsonify(message="Maison supprimée avec succès"), 204


# --- CRUD pour les Chambres (restent les mêmes, mais la sérialisation est améliorée et filtrage pour user story 2 & 7) ---

@api_bp.route('/chambres', methods=['POST'])
def create_chambre():
    data = request.get_json()
    if not data or not all(k in data for k in ['maison_id', 'titre', 'prix', 'taille', 'type']):
        abort(400, description="maison_id, titre, prix, taille, et type sont requis.")

    if not Maison.query.get(data['maison_id']):
        abort(404, description="La maison spécifiée n'existe pas.")

    new_chambre = Chambre(
        maison_id=data['maison_id'],
        titre=data['titre'],
        description=data.get('description'),
        taille=data['taille'],
        type=data['type'],
        meublee=data.get('meublee', False),
        salle_de_bain=data.get('salle_de_bain', False),
        prix=data['prix'],
        disponible=data.get('disponible', True)
    )
    db.session.add(new_chambre)
    db.session.commit()
    return jsonify(serialize_chambre(new_chambre)), 201


@api_bp.route('/chambres', methods=['GET'])
def get_chambres():
    # User Story 2 & 7: Filtrer par proprietaire_id si spécifié
    proprietaire_id = request.args.get('proprietaire_id', type=int)
    query = Chambre.query.options(db.joinedload(Chambre.maison).joinedload(Maison.proprietaire),
                                  db.joinedload(Chambre.medias))

    if proprietaire_id:
        # Filtrer les chambres qui appartiennent à une maison de ce propriétaire
        query = query.join(Maison).filter(Maison.proprietaire_id == proprietaire_id)

    chambres = query.all()
    return jsonify([serialize_chambre(c) for c in chambres]), 200


@api_bp.route('/chambres/<int:chambre_id>', methods=['GET'])
def get_chambre(chambre_id):
    # Charger la chambre avec sa maison, son propriétaire et ses médias
    chambre = Chambre.query.options(
        db.joinedload(Chambre.maison).joinedload(Maison.proprietaire),
        db.joinedload(Chambre.medias)
    ).get_or_404(chambre_id)
    return jsonify(serialize_chambre(chambre)), 200


@api_bp.route('/chambres/<int:chambre_id>', methods=['PUT'])
def update_chambre(chambre_id):
    chambre = Chambre.query.get_or_404(chambre_id)
    data = request.get_json()

    if not data:
        abort(400, description="Données de mise à jour requises.")

    chambre.titre = data.get('titre', chambre.titre)
    chambre.description = data.get('description', chambre.description)
    chambre.taille = data.get('taille', chambre.taille)
    chambre.type = data.get('type', chambre.type)
    chambre.meublee = data.get('meublee', chambre.meublee)
    chambre.salle_de_bain = data.get('salle_de_bain', chambre.salle_de_bain)
    chambre.prix = data.get('prix', chambre.prix)
    chambre.disponible = data.get('disponible', chambre.disponible)

    if 'maison_id' in data and data['maison_id'] != chambre.maison_id:
        if not Maison.query.get(data['maison_id']):
            abort(404, description="La nouvelle maison spécifiée n'existe pas.")
        chambre.maison_id = data['maison_id']

    try:
        db.session.commit()
        return jsonify(serialize_chambre(chambre)), 200
    except Exception as e:
        db.session.rollback()
        abort(500, description=f"Erreur lors de la mise à jour de la chambre: {str(e)}")


@api_bp.route('/chambres/<int:chambre_id>', methods=['DELETE'])
def delete_chambre(chambre_id):
    chambre = Chambre.query.get_or_404(chambre_id)
    db.session.delete(chambre)
    db.session.commit()
    return jsonify(message="Chambre supprimée avec succès"), 204


# --- CRUD pour les Contrats (User Story 5) ---

@api_bp.route('/contrats', methods=['POST'])
def create_contrat():
    data = request.get_json()
    if not data or not all(k in data for k in
                           ['locataire_id', 'chambre_id', 'date_debut', 'date_fin', 'montant_caution', 'periodicite',
                            'mode_paiement']):
        abort(400,
              description="locataire_id, chambre_id, date_debut, date_fin, montant_caution, periodicite, et mode_paiement sont requis.")

    # Vérifier si locataire et chambre existent
    if not Utilisateur.query.get(data['locataire_id']):
        abort(404, description="Le locataire spécifié n'existe pas.")
    if not Chambre.query.get(data['chambre_id']):
        abort(404, description="La chambre spécifiée n'existe pas.")

    # Convertir les dates
    try:
        date_debut = date.fromisoformat(data['date_debut'])
        date_fin = date.fromisoformat(data['date_fin'])
    except ValueError:
        abort(400, description="Format de date invalide. Utilisez YYYY-MM-DD.")

    new_contrat = Contrat(
        locataire_id=data['locataire_id'],
        chambre_id=data['chambre_id'],
        date_debut=date_debut,
        date_fin=date_fin,
        montant_caution=data['montant_caution'],
        mois_caution=data.get('mois_caution'),
        description=data.get('description'),
        mode_paiement=data['mode_paiement'],
        periodicite=data['periodicite'],
        statut=data.get('statut', 'actif')  # Statut par défaut 'actif'
    )
    db.session.add(new_contrat)
    db.session.commit()
    return jsonify(serialize_contrat(new_contrat)), 201


@api_bp.route('/contrats', methods=['GET'])
def get_contrats():
    query = Contrat.query.options(
        db.joinedload(Contrat.locataire),  # Charge les données du locataire
        db.joinedload(Contrat.chambre).joinedload(Chambre.maison).joinedload(Maison.proprietaire)
        # Charge la chambre et ses relations imbriquées
    )

    # Ici, tu peux ajouter des filtres si tu en as besoin, par exemple par locataire_id, statut, etc.
    # Exemple de filtre:
    statut_filter = request.args.get('statut')
    if statut_filter:
        query = query.filter_by(statut=statut_filter)

    contrats = query.all()
    return jsonify([serialize_contrat(c) for c in contrats]), 200


@api_bp.route('/contrats/<int:contrat_id>', methods=['GET'])
# def get_contrat(contrat_id):
#     contrat = Contrat.query.options(
#         db.joinedload(Contrat.locataire),  # Charge les données du locataire
#         db.joinedload(Contrat.chambre).joinedload(Chambre.maison).joinedload(Maison.proprietaire)
#     ).filter_by(id=contrat_id).first_or_404()  # Utilise filter_by et first_or_404
#
#     return jsonify(serialize_contrat(contrat)), 200
def get_contract_details(contrat_id):
    contrat = Contrat.query.get(contrat_id)
    if not contrat:
        return jsonify({"message": "Contrat non trouvé."}), 404

    # Calcul du montant total attendu du contrat
    total_expected_amount = 0.0  # Initialise en float pour être cohérent
    if contrat.chambre and contrat.chambre.prix and contrat.date_debut and contrat.date_fin:
        start_date = contrat.date_debut
        end_date = contrat.date_fin

        delta = relativedelta(end_date, start_date)
        num_months = delta.years * 12 + delta.months
        if delta.days > 0:
            num_months += 1

        total_expected_amount = float(contrat.chambre.prix) * num_months
    else:
        total_expected_amount = 0.0

    # Calcul du montant total payé
    total_paid_amount_decimal = db.session.query(db.func.sum(Paiement.montant)).filter(
        Paiement.contrat_id == contrat_id,
        Paiement.statut == 'payé'
    ).scalar() or 0.0

    # Convertir total_paid_amount_decimal en float avant la soustraction
    total_paid_amount = float(total_paid_amount_decimal)  # <--- MODIFICATION ICI

    # Calcul du solde restant
    remaining_balance = total_expected_amount - total_paid_amount

    # Sérialisation du contrat (similaire à ce que tu as déjà)
    chambre_data = None
    if contrat.chambre:
        maison_data = None
        if contrat.chambre.maison:
            proprietaire_maison_data = None
            if contrat.chambre.maison.proprietaire:
                proprietaire_maison_data = {
                    "id": contrat.chambre.maison.proprietaire.id,
                    "nom_utilisateur": contrat.chambre.maison.proprietaire.nom_utilisateur,
                    "email": contrat.chambre.maison.proprietaire.email,
                    "telephone": contrat.chambre.maison.proprietaire.telephone,
                    "cni": contrat.chambre.maison.proprietaire.cni,
                    "role": contrat.chambre.maison.proprietaire.role,
                    "cree_le": contrat.chambre.maison.proprietaire.cree_le.isoformat() if contrat.chambre.maison.proprietaire.cree_le else None
                }
            maison_data = {
                "id": contrat.chambre.maison.id,
                "adresse": contrat.chambre.maison.adresse,
                "description": contrat.chambre.maison.description,
                "latitude": str(contrat.chambre.maison.latitude),
                "longitude": str(contrat.chambre.maison.longitude),
                "proprietaire_id": contrat.chambre.maison.proprietaire_id,
                "proprietaire": proprietaire_maison_data,
                "cree_le": contrat.chambre.maison.cree_le.isoformat() if contrat.chambre.maison.cree_le else None
            }

        medias_data = []
        for media in contrat.chambre.medias:
            medias_data.append({
                "id": media.id,
                "chambre_id": media.chambre_id,
                "url": media.url,
                "type": media.type,
                "description": media.description,
                "cree_le": media.cree_le.isoformat() if media.cree_le else None
            })

        chambre_data = {
            "id": contrat.chambre.id,
            "titre": contrat.chambre.titre,
            "description": contrat.chambre.description,
            "prix": str(contrat.chambre.prix),
            "taille": contrat.chambre.taille,
            "type": contrat.chambre.type,
            "meublee": contrat.chambre.meublee,
            "salle_de_bain": contrat.chambre.salle_de_bain,
            "disponible": contrat.chambre.disponible,
            "maison_id": contrat.chambre.maison_id,
            "maison": maison_data,
            "medias": medias_data,
            "cree_le": contrat.chambre.cree_le.isoformat() if contrat.chambre.cree_le else None
        }

    locataire_data = None
    if contrat.locataire:
        locataire_data = {
            "id": contrat.locataire.id,
            "nom_utilisateur": contrat.locataire.nom_utilisateur,
            "email": contrat.locataire.email,
            "telephone": contrat.locataire.telephone,
            "cni": contrat.locataire.cni,
            "role": contrat.locataire.role,
            "cree_le": contrat.locataire.cree_le.isoformat() if contrat.locataire.cree_le else None
        }

    return jsonify({
        "id": contrat.id,
        "chambre_id": contrat.chambre_id,
        "locataire_id": contrat.locataire_id,
        "date_debut": contrat.date_debut.isoformat() if contrat.date_debut else None,
        "date_fin": contrat.date_fin.isoformat() if contrat.date_fin else None,
        "description": contrat.description,
        "montant_caution": str(contrat.montant_caution),
        "mois_caution": contrat.mois_caution,
        "periodicite": contrat.periodicite,
        "mode_paiement": contrat.mode_paiement,
        "statut": contrat.statut,
        "cree_le": contrat.cree_le.isoformat() if contrat.cree_le else None,
        "chambre": chambre_data,
        "locataire": locataire_data,
        "total_expected_amount": total_expected_amount,  # <-- AJOUTE CETTE LIGNE
        "total_paid_amount": total_paid_amount,  # <-- AJOUTE CETTE LIGNE
        "remaining_balance": remaining_balance  # <-- AJOUTE CETTE LIGNE
    }), 200


@api_bp.route('/contrats/<int:contrat_id>', methods=['PUT'])
def update_contrat(contrat_id):
    contrat = Contrat.query.get_or_404(contrat_id)
    data = request.get_json()

    if not data:
        abort(400, description="Données de mise à jour requises.")

    if 'locataire_id' in data and data['locataire_id'] != contrat.locataire_id:
        if not Utilisateur.query.get(data['locataire_id']):
            abort(404, description="Le nouveau locataire spécifié n'existe pas.")
        contrat.locataire_id = data['locataire_id']

    if 'chambre_id' in data and data['chambre_id'] != contrat.chambre_id:
        if not Chambre.query.get(data['chambre_id']):
            abort(404, description="La nouvelle chambre spécifiée n'existe pas.")
        contrat.chambre_id = data['chambre_id']

    if 'date_debut' in data:
        try:
            contrat.date_debut = date.fromisoformat(data['date_debut'])
        except ValueError:
            abort(400, description="Format de date de début invalide. Utilisez YYYY-MM-DD.")
    if 'date_fin' in data:
        try:
            contrat.date_fin = date.fromisoformat(data['date_fin'])
        except ValueError:
            abort(400, description="Format de date de fin invalide. Utilisez YYYY-MM-DD.")

    contrat.montant_caution = data.get('montant_caution', contrat.montant_caution)
    contrat.mois_caution = data.get('mois_caution', contrat.mois_caution)
    contrat.description = data.get('description', contrat.description)
    contrat.mode_paiement = data.get('mode_paiement', contrat.mode_paiement)
    contrat.periodicite = data.get('periodicite', contrat.periodicite)
    contrat.statut = data.get('statut', contrat.statut)

    try:
        db.session.commit()
        return jsonify(serialize_contrat(contrat)), 200
    except Exception as e:
        db.session.rollback()
        abort(500, description=f"Erreur lors de la mise à jour du contrat: {str(e)}")


@api_bp.route('/contrats/<int:contrat_id>', methods=['DELETE'])
def delete_contrat(contrat_id):
    contrat = Contrat.query.get_or_404(contrat_id)
    db.session.delete(contrat)
    db.session.commit()
    return jsonify(message="Contrat supprimé avec succès"), 204


# --- CRUD pour les Paiements (User Story 3 & 4) ---

@api_bp.route('/paiements', methods=['POST'])
def create_paiement():
    data = request.get_json()
    if not data:
        return jsonify({"message": "Données JSON requises"}), 400

    contrat_id = data.get('contrat_id')
    montant = data.get('montant')
    date_echeance_str = data.get('date_echeance')  # <--- RÉCUPÈRE LA NOUVELLE DATE D'ÉCHÉANCE
    date_paiement_str = data.get('date_paiement')  # Peut être null si impayé
    statut = data.get('statut', 'impayé')  # Statut par défaut 'impayé' si date_paiement est null

    # Mettre à jour la validation des champs obligatoires
    if not all([contrat_id, montant, date_echeance_str]):  # <--- date_echeance_str devient obligatoire
        return jsonify({"message": "Les champs 'contrat_id', 'montant' et 'date_echeance' sont obligatoires."}), 400

    try:
        contrat = Contrat.query.get(contrat_id)
        if not contrat:
            return jsonify({"message": "Contrat non trouvé."}), 404

        # Convertir les dates
        date_echeance = datetime.strptime(date_echeance_str, '%Y-%m-%d').date()  # Stocke juste la date
        date_paiement = None
        if date_paiement_str:  # La date de paiement est optionnelle
            date_paiement = datetime.strptime(date_paiement_str,
                                              '%Y-%m-%d')  # Peut être datetime ou juste date selon ta précision

        # Ajuster le statut si date_paiement est fourni
        if date_paiement and statut == 'impayé':  # Si une date de paiement est donnée, mais le statut est impayé, force à payé.
            statut = 'payé'

        new_paiement = Paiement(
            contrat_id=contrat_id,
            montant=montant,
            date_echeance=date_echeance,  # <--- AJOUTE LA DATE D'ÉCHÉANCE ICI
            date_paiement=date_paiement,
            statut=statut
        )
        db.session.add(new_paiement)
        db.session.commit()

        # Mettre à jour la réponse JSON
        return jsonify({
            "message": "Paiement créé avec succès",
            "paiement": {
                "id": new_paiement.id,
                "contrat_id": new_paiement.contrat_id,
                "montant": float(new_paiement.montant),
                "date_echeance": new_paiement.date_echeance.isoformat(),  # <--- AJOUTE À LA RÉPONSE
                "date_paiement": new_paiement.date_paiement.isoformat() if new_paiement.date_paiement else None,
                "statut": new_paiement.statut,
                "cree_le": new_paiement.cree_le.isoformat()
            }
        }), 201

    except ValueError as e:
        return jsonify({"message": f"Format de date invalide. Utilisez YYYY-MM-DD. Détails: {str(e)}"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Erreur interne du serveur: {str(e)}"}), 500


@api_bp.route('/paiements', methods=['GET'])
def get_paiements():
    # User Story 3 & 4: Filtrage par statut et propriétaire
    statut_filter = request.args.get('statut')  # 'payé' | 'impayé'
    proprietaire_id = request.args.get('proprietaire_id', type=int)

    query = Paiement.query.options(
        db.joinedload(Paiement.contrat).joinedload(Contrat.chambre).joinedload(Chambre.maison).joinedload(
            Maison.proprietaire)
    )

    if statut_filter:
        query = query.filter_by(statut=statut_filter)

    if proprietaire_id:
        query = query.join(Contrat).join(Chambre).join(Maison).filter(Maison.proprietaire_id == proprietaire_id)

    paiements = query.all()
    return jsonify([serialize_paiement(p) for p in paiements]), 200


@api_bp.route('/paiements/<int:paiement_id>', methods=['GET'])
def get_paiement(paiement_id):
    paiement = Paiement.query.get_or_404(paiement_id)
    return jsonify(serialize_paiement(paiement)), 200


@api_bp.route('/paiements/<int:paiement_id>', methods=['PUT'])
def update_paiement(paiement_id):
    paiement = Paiement.query.get(paiement_id)
    if not paiement:
        return jsonify({"message": "Paiement non trouvé."}), 404

    data = request.get_json()

    # Mise à jour du montant
    if 'montant' in data:
        try:
            # Convertir en Decimal pour correspondre au type de la base de données
            paiement.montant = Decimal(str(data['montant']))
        except Exception as e:
            return jsonify({"message": f"Montant invalide: {e}"}), 400

    # Mise à jour de la date d'échéance
    if 'date_echeance' in data:
        try:
            paiement.date_echeance = datetime.strptime(data['date_echeance'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"message": "Format de date d'échéance invalide. Utilisez YYYY-MM-DD."}), 400

    # Mise à jour de la date de paiement (peut être null)
    if 'date_paiement' in data:
        if data['date_paiement'] is None:
            paiement.date_paiement = None
        else:
            try:
                paiement.date_paiement = datetime.strptime(data['date_paiement'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({"message": "Format de date de paiement invalide. Utilisez YYYY-MM-DD ou null."}), 400

    # Mise à jour du statut (déduit si date_paiement est fournie ou non)
    # Si date_paiement est fournie, le statut devient 'payé', sinon 'impayé'
    # On peut aussi permettre de le définir explicitement si besoin, mais la déduction est plus robuste.
    if 'statut' in data:
        paiement.statut = data['statut']
    else:  # Déduire le statut si non fourni explicitement
        paiement.statut = 'payé' if paiement.date_paiement else 'impayé'

    try:
        db.session.commit()
        return jsonify({
            "id": paiement.id,
            "contrat_id": paiement.contrat_id,
            "montant": str(paiement.montant),
            "date_echeance": paiement.date_echeance.isoformat(),
            "date_paiement": paiement.date_paiement.isoformat() if paiement.date_paiement else None,
            "statut": paiement.statut,
            "cree_le": paiement.cree_le.isoformat()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Erreur lors de la mise à jour du paiement: {str(e)}"}), 500


@api_bp.route('/paiements/<int:paiement_id>', methods=['DELETE'])
def delete_paiement(paiement_id):
    paiement = Paiement.query.get(paiement_id)
    if not paiement:
        return jsonify({"message": "Paiement non trouvé."}), 404

    try:
        db.session.delete(paiement)
        db.session.commit()
        return jsonify({"message": "Paiement supprimé avec succès."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Erreur lors de la suppression du paiement: {str(e)}"}), 500


@api_bp.route('/contrats/<int:contrat_id>/paiements', methods=['GET'])
def get_paiements_by_contrat(contrat_id):
    contrat = Contrat.query.get(contrat_id)
    if not contrat:
        return jsonify({"message": "Contrat non trouvé."}), 404

    paiements = Paiement.query.filter_by(contrat_id=contrat_id).order_by(
        Paiement.date_echeance.desc()).all()  # Trie par date d'échéance

    paiements_data = []
    for paiement in paiements:
        paiements_data.append({
            "id": paiement.id,
            "contrat_id": paiement.contrat_id,
            "montant": float(paiement.montant),
            "date_echeance": paiement.date_echeance.isoformat(),  # <--- AJOUTE À LA RÉPONSE GET
            "date_paiement": paiement.date_paiement.isoformat() if paiement.date_paiement else None,
            "statut": paiement.statut,
            "cree_le": paiement.cree_le.isoformat()
        })
    return jsonify(paiements_data), 200


# --- CRUD pour les Rendez-vous (User Story 8) ---

@api_bp.route('/rendezvous', methods=['POST'])
def create_rendezvous():
    data = request.get_json()
    if not data or not all(k in data for k in ['locataire_id', 'chambre_id', 'date_heure']):
        abort(400, description="locataire_id, chambre_id, et date_heure sont requis.")

    if not Utilisateur.query.get(data['locataire_id']):
        abort(404, description="Le locataire spécifié n'existe pas.")
    if not Chambre.query.get(data['chambre_id']):
        abort(404, description="La chambre spécifiée n'existe pas.")

    try:
        date_heure = datetime.fromisoformat(data['date_heure'])
    except ValueError:
        abort(400, description="Format de date/heure invalide. Utilisez YYYY-MM-DDTHH:MM:SS.")

    new_rendezvous = RendezVous(
        locataire_id=data['locataire_id'],
        chambre_id=data['chambre_id'],
        date_heure=date_heure,
        statut=data.get('statut', 'en_attente')  # Statut par défaut
    )
    db.session.add(new_rendezvous)
    db.session.commit()
    return jsonify(serialize_rendez_vous(new_rendezvous)), 201


@api_bp.route('/rendezvous', methods=['GET'])
def get_rendezvous():
    rendezvous = RendezVous.query.all()
    return jsonify([serialize_rendez_vous(r) for r in rendezvous]), 200


@api_bp.route('/rendezvous/<int:rendezvous_id>', methods=['GET'])
def get_single_rendezvous(rendezvous_id):
    rendezvous = RendezVous.query.get_or_404(rendezvous_id)
    return jsonify(serialize_rendez_vous(rendezvous)), 200


@api_bp.route('/rendezvous/<int:rendezvous_id>', methods=['PUT'])
def update_rendezvous(rendezvous_id):
    rendezvous = RendezVous.query.get_or_404(rendezvous_id)
    data = request.get_json()

    if not data:
        abort(400, description="Données de mise à jour requises.")

    if 'locataire_id' in data and data['locataire_id'] != rendezvous.locataire_id:
        if not Utilisateur.query.get(data['locataire_id']):
            abort(404, description="Le nouveau locataire spécifié n'existe pas.")
        rendezvous.locataire_id = data['locataire_id']

    if 'chambre_id' in data and data['chambre_id'] != rendezvous.chambre_id:
        if not Chambre.query.get(data['chambre_id']):
            abort(404, description="La nouvelle chambre spécifiée n'existe pas.")
        rendezvous.chambre_id = data['chambre_id']

    if 'date_heure' in data:
        try:
            rendezvous.date_heure = datetime.fromisoformat(data['date_heure'])
        except ValueError:
            abort(400, description="Format de date/heure invalide. Utilisez YYYY-MM-DDTHH:MM:SS.")

    rendezvous.statut = data.get('statut', rendezvous.statut)

    try:
        db.session.commit()
        return jsonify(serialize_rendez_vous(rendezvous)), 200
    except Exception as e:
        db.session.rollback()
        abort(500, description=f"Erreur lors de la mise à jour du rendez-vous: {str(e)}")


@api_bp.route('/rendezvous/<int:rendezvous_id>', methods=['DELETE'])
def delete_rendezvous(rendezvous_id):
    rendezvous = RendezVous.query.get_or_404(rendezvous_id)
    db.session.delete(rendezvous)
    db.session.commit()
    return jsonify(message="Rendez-vous supprimé avec succès"), 204


# --- CRUD pour les Médias (User Story 9) ---

@api_bp.route('/medias', methods=['POST'])
def create_media():
    data = request.get_json()
    if not data or not all(k in data for k in ['chambre_id', 'url', 'type']):
        abort(400, description="chambre_id, url, et type sont requis.")

    if not Chambre.query.get(data['chambre_id']):
        abort(404, description="La chambre spécifiée n'existe pas.")

    new_media = Media(
        chambre_id=data['chambre_id'],
        url=data['url'],
        type=data['type'],
        description=data.get('description')
    )
    db.session.add(new_media)
    db.session.commit()
    return jsonify(serialize_media(new_media)), 201


@api_bp.route('/medias', methods=['GET'])
def get_medias():
    medias = Media.query.all()
    return jsonify([serialize_media(m) for m in medias]), 200


@api_bp.route('/medias/<int:media_id>', methods=['GET'])
def get_media(media_id):
    media = Media.query.get_or_404(media_id)
    return jsonify(serialize_media(media)), 200


@api_bp.route('/medias/<int:media_id>', methods=['PUT'])
def update_media(media_id):
    media = Media.query.get_or_404(media_id)
    data = request.get_json()

    if not data:
        abort(400, description="Données de mise à jour requises.")

    if 'chambre_id' in data and data['chambre_id'] != media.chambre_id:
        if not Chambre.query.get(data['chambre_id']):
            abort(404, description="La nouvelle chambre spécifiée n'existe pas.")
        media.chambre_id = data['chambre_id']

    media.url = data.get('url', media.url)
    media.type = data.get('type', media.type)
    media.description = data.get('description', media.description)

    try:
        db.session.commit()
        return jsonify(serialize_media(media)), 200
    except Exception as e:
        db.session.rollback()
        abort(500, description=f"Erreur lors de la mise à jour du média: {str(e)}")


@api_bp.route('/medias/<int:media_id>', methods=['DELETE'])
def delete_media(media_id):
    media = Media.query.get_or_404(media_id)
    db.session.delete(media)
    db.session.commit()
    return jsonify(message="Média supprimé avec succès"), 204
