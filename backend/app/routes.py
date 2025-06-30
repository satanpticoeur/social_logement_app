from datetime import datetime, date  # Ajout de date pour les champs Date

from flask import Blueprint, jsonify, request, abort

from app import db
from app.models import Utilisateur, Maison, Chambre, Contrat, Paiement, RendezVous, Media

api_bp = Blueprint('api', __name__)


# --- Routes de test initiales (tu peux les garder ou les retirer si tu n'en as plus besoin) ---
@api_bp.route('/')
def index():
    return jsonify(message="Bienvenue sur l'API Social Logement !"), 200


@api_bp.route('/test')
def test_route():
    return jsonify(data="Ceci est une route de test de l'API."), 200


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
        "mode_paiement": contrat.mode_paiement,
        "cree_le": contrat.cree_le.isoformat() if contrat.cree_le else None,
        # Inclure le locataire et la chambre si joints
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
    contrats = Contrat.query.all()
    return jsonify([serialize_contrat(c) for c in contrats]), 200


@api_bp.route('/contrats/<int:contrat_id>', methods=['GET'])
def get_contrat(contrat_id):
    contrat = Contrat.query.get_or_404(contrat_id)
    return jsonify(serialize_contrat(contrat)), 200


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
    if not data or not all(k in data for k in ['contrat_id', 'montant', 'statut', 'date_echeance']):
        abort(400, description="contrat_id, montant, statut, et date_echeance sont requis.")

    if not Contrat.query.get(data['contrat_id']):
        abort(404, description="Le contrat spécifié n'existe pas.")

    try:
        date_echeance = date.fromisoformat(data['date_echeance'])
        date_paiement = date.fromisoformat(data['date_paiement']) if data.get('date_paiement') else None
    except ValueError:
        abort(400, description="Format de date invalide. Utilisez YYYY-MM-DD.")

    new_paiement = Paiement(
        contrat_id=data['contrat_id'],
        montant=data['montant'],
        statut=data['statut'],
        date_echeance=date_echeance,
        date_paiement=date_paiement
    )
    db.session.add(new_paiement)
    db.session.commit()
    return jsonify(serialize_paiement(new_paiement)), 201


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
    paiement = Paiement.query.get_or_404(paiement_id)
    data = request.get_json()

    if not data:
        abort(400, description="Données de mise à jour requises.")

    if 'contrat_id' in data and data['contrat_id'] != paiement.contrat_id:
        if not Contrat.query.get(data['contrat_id']):
            abort(404, description="Le nouveau contrat spécifié n'existe pas.")
        paiement.contrat_id = data['contrat_id']

    paiement.montant = data.get('montant', paiement.montant)
    paiement.statut = data.get('statut', paiement.statut)

    if 'date_echeance' in data:
        try:
            paiement.date_echeance = date.fromisoformat(data['date_echeance'])
        except ValueError:
            abort(400, description="Format de date d'échéance invalide. Utilisez YYYY-MM-DD.")
    if 'date_paiement' in data:
        try:
            paiement.date_paiement = date.fromisoformat(data['date_paiement']) if data['date_paiement'] else None
        except ValueError:
            abort(400, description="Format de date de paiement invalide. Utilisez YYYY-MM-DD ou null.")

    try:
        db.session.commit()
        return jsonify(serialize_paiement(paiement)), 200
    except Exception as e:
        db.session.rollback()
        abort(500, description=f"Erreur lors de la mise à jour du paiement: {str(e)}")


@api_bp.route('/paiements/<int:paiement_id>', methods=['DELETE'])
def delete_paiement(paiement_id):
    paiement = Paiement.query.get_or_404(paiement_id)
    db.session.delete(paiement)
    db.session.commit()
    return jsonify(message="Paiement supprimé avec succès"), 204


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
    return jsonify(serialize_rendezvous(new_rendezvous)), 201


@api_bp.route('/rendezvous', methods=['GET'])
def get_rendezvous():
    rendezvous = RendezVous.query.all()
    return jsonify([serialize_rendezvous(r) for r in rendezvous]), 200


@api_bp.route('/rendezvous/<int:rendezvous_id>', methods=['GET'])
def get_single_rendezvous(rendezvous_id):
    rendezvous = RendezVous.query.get_or_404(rendezvous_id)
    return jsonify(serialize_rendezvous(rendezvous)), 200


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
        return jsonify(serialize_rendezvous(rendezvous)), 200
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
