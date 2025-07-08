from datetime import timedelta, datetime, date

from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models import Chambre, Maison, Contrat, Utilisateur, Paiement
from flask_jwt_extended import jwt_required, get_jwt_identity
import json
from sqlalchemy.orm import joinedload  # Import joinedload here

from app.serialization import serialize_media  # Add others if needed for other routes

locataire_bp = Blueprint('locataire', __name__, url_prefix='/api/locataire')


@locataire_bp.route('/chambres/recherche', methods=['GET'])
# @jwt_required()
def search_chambres():
    ville = request.args.get('ville')
    min_prix = request.args.get('min_prix', type=float)
    max_prix = request.args.get('max_prix', type=float)
    type_chambre = request.args.get('type')
    meublee = request.args.get('meublee')
    disponible = request.args.get('disponible', type=bool, default=True)

    # Use joinedload for optimization
    query = Chambre.query.join(Maison) \
        .options(joinedload(Chambre.maison)) \
        .options(joinedload(Chambre.medias))

    if ville:
        query = query.filter(Maison.ville.ilike(f'%{ville}%'))
    if min_prix is not None:
        query = query.filter(Chambre.prix >= min_prix)
    if max_prix is not None:
        query = query.filter(Chambre.prix <= max_prix)
    if type_chambre:
        query = query.filter(Chambre.type.ilike(f'%{type_chambre}%'))
    if meublee is not None:
        if isinstance(meublee, str):
            meublee = meublee.lower() == 'true'
        query = query.filter(Chambre.meublee == meublee)
    if disponible is not None:
        if isinstance(disponible, str):
            disponible = disponible.lower() == 'true'
        query = query.filter(Chambre.disponible == disponible)

    chambres = query.all()

    if not chambres:
        return jsonify({"message": "Aucune chambre trouvée avec ces critères."}), 404

    results = []
    for chambre in chambres:
        # Using serialize_media from app.serialization
        medias_data = [serialize_media(media) for media in chambre.medias] if hasattr(chambre, 'medias') else []

        results.append({
            "id": chambre.id,
            "maison_id": chambre.maison_id,
            "adresse_maison": chambre.maison.adresse if chambre.maison else None,
            "ville_maison": chambre.maison.ville if chambre.maison else None,
            "titre": chambre.titre,
            "description": chambre.description,
            "taille": chambre.taille,
            "type": chambre.type,
            "meublee": chambre.meublee,
            "salle_de_bain": chambre.salle_de_bain,
            "prix": float(chambre.prix),
            "disponible": chambre.disponible,
            "medias": medias_data,
            "cree_le": chambre.cree_le.isoformat()
        })

    return jsonify(results), 200


# Route pour obtenir les détails d'une chambre spécifique (par son ID)
@locataire_bp.route('/chambres/<int:chambre_id>', methods=['GET'])
# @jwt_required()
def get_chambre_details(chambre_id):
    # Load chambre with its relations for serialization
    chambre = Chambre.query.options(joinedload(Chambre.maison), joinedload(Chambre.medias)).get(chambre_id)

    if not chambre or not chambre.disponible:
        return jsonify({"message": "Chambre non trouvée ou non disponible."}), 404

    # Using serialize_media from app.serialization
    medias_data = [serialize_media(media) for media in chambre.medias] if hasattr(chambre, 'medias') else []

    return jsonify({
        "id": chambre.id,
        "maison_id": chambre.maison_id,
        "adresse_maison": chambre.maison.adresse if chambre.maison else None,
        "ville_maison": chambre.maison.ville if chambre.maison else None,
        "titre": chambre.titre,
        "description": chambre.description,
        "taille": chambre.taille,
        "type": chambre.type,
        "meublee": chambre.meublee,
        "salle_de_bain": chambre.salle_de_bain,
        "prix": float(chambre.prix),
        "disponible": chambre.disponible,
        "cree_le": chambre.cree_le.isoformat(),
        "medias": medias_data
    }), 200


# Utility function to generate payments (can be placed here or in a utils.py file)
def generer_paiements_contrat(contrat: Contrat):
    """
    Génère les paiements mensuels pour un contrat donné.
    """
    paiements_generes = []
    current_date = contrat.date_debut
    loyer_mensuel = contrat.chambre.prix

    if contrat.montant_caution and contrat.montant_caution > 0:
        paiement_caution = Paiement(
            contrat_id=contrat.id,
            montant=contrat.montant_caution,
            date_echeance=contrat.date_debut,
            statut='impayé',
            description="Paiement de la caution"
        )
        db.session.add(paiement_caution)
        paiements_generes.append(paiement_caution)

    while current_date <= contrat.date_fin:
        paiement_loyer = Paiement(
            contrat_id=contrat.id,
            montant=loyer_mensuel,
            date_echeance=current_date,
            statut='impayé',
            description=f"Loyer du mois de {current_date.strftime('%B %Y')}"
        )
        db.session.add(paiement_loyer)
        paiements_generes.append(paiement_loyer)

        year = current_date.year
        month = current_date.month + 1
        if month > 12:
            month = 1
            year += 1
        try:
            current_date = date(year, month, current_date.day)
        except ValueError:
            current_date = date(year, month, 1) + timedelta(days=-1)

    return paiements_generes


@locataire_bp.route('/chambres/<int:chambre_id>/louer', methods=['POST'])
@jwt_required()
def louer_chambre(chambre_id):
    current_user_identity = get_jwt_identity()
    locataire_id = json.loads(current_user_identity)['id']

    locataire = Utilisateur.query.get(locataire_id)
    if not locataire or locataire.role != 'locataire':
        return jsonify({"message": "Accès refusé. Seuls les locataires peuvent louer une chambre."}), 403

    chambre = Chambre.query.get(chambre_id)
    if not chambre:
        return jsonify({"message": "Chambre non trouvée."}), 404
    if not chambre.disponible:
        return jsonify({"message": "Cette chambre n'est plus disponible."}), 400

    data = request.get_json()
    date_debut_contrat_str = data.get('date_debut')
    duree_mois = data.get('duree_mois', 12)

    if not date_debut_contrat_str:
        return jsonify({"message": "La date de début du contrat est obligatoire."}), 400

    try:
        date_debut_contrat = datetime.strptime(date_debut_contrat_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"message": "Format de date de début invalide. Utilisez YYYY-MM-DD."}), 400

    date_fin_contrat = date_debut_contrat
    for _ in range(duree_mois):
        year, month = date_fin_contrat.year, date_fin_contrat.month
        month += 1
        if month > 12:
            month = 1
            year += 1
        try:
            date_fin_contrat = date(year, month, date_fin_contrat.day)
        except ValueError:
            date_fin_contrat = date(year, month, 1) - timedelta(days=1)

    date_fin_contrat = date_fin_contrat - timedelta(days=1)

    montant_caution = data.get('montant_caution', float(chambre.prix) * 2)
    mois_caution = data.get('mois_caution', 2)
    mode_paiement = data.get('mode_paiement', 'virement_bancaire')
    periodicite = data.get('periodicite', 'mensuel')

    try:
        db.session.begin_nested()

        chambre.disponible = False
        db.session.add(chambre)

        new_contrat = Contrat(
            locataire_id=locataire_id,
            chambre_id=chambre_id,
            date_debut=date_debut_contrat,
            date_fin=date_fin_contrat,
            montant_caution=montant_caution,
            mois_caution=mois_caution,
            mode_paiement=mode_paiement,
            periodicite=periodicite,
            statut='actif',
            description=f"Contrat de location pour la chambre '{chambre.titre}' du {date_debut_contrat.isoformat()} au {date_fin_contrat.isoformat()}."
        )
        db.session.add(new_contrat)
        db.session.flush()

        generer_paiements_contrat(new_contrat)

        db.session.commit()

        return jsonify({
            "message": "Chambre louée avec succès et contrat, incluant l'échéancier des paiements, généré !",
            "chambre_id": chambre.id,
            "contrat_id": new_contrat.id,
            "chambre_disponible": chambre.disponible
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(
            f"Erreur lors de la location de la chambre {chambre_id} ou génération des paiements: {e}")
        return jsonify(
            {"message": "Erreur lors de la location de la chambre. Veuillez réessayer.", "error": str(e)}), 500


@locataire_bp.route('/contrats', methods=['GET'])
@jwt_required()
def get_locataire_contrats():
    current_user_identity = get_jwt_identity()
    locataire_id = json.loads(current_user_identity)['id']

    contrats = Contrat.query.filter_by(locataire_id=locataire_id).order_by(Contrat.date_debut.desc()).all()

    results = []
    for contrat in contrats:
        chambre = contrat.chambre
        maison = chambre.maison if chambre else None

        results.append({
            "id": contrat.id,
            "chambre_id": chambre.id if chambre else None,
            "chambre_titre": chambre.titre if chambre else None,
            "chambre_adresse": f"{maison.adresse}, {maison.ville}" if maison else None,
            "prix_mensuel_chambre": float(chambre.prix) if chambre and chambre.prix else None,
            "date_debut": contrat.date_debut.isoformat(),
            "date_fin": contrat.date_fin.isoformat(),
            "montant_caution": float(contrat.montant_caution) if contrat.montant_caution else None,
            "mois_caution": contrat.mois_caution,
            "mode_paiement": contrat.mode_paiement,
            "periodicite": contrat.periodicite,
            "statut": contrat.statut,
            "description": contrat.description,
            "cree_le": contrat.cree_le.isoformat(),
        })
    return jsonify(results), 200


# Endpoint to get details of a specific contract for the tenant
@locataire_bp.route('/contrats/<int:contrat_id>', methods=['GET'])
@jwt_required()
def get_locataire_contrat_details(contrat_id):
    current_user_identity = get_jwt_identity()
    locataire_id = json.loads(current_user_identity)['id']

    contrat = Contrat.query.filter_by(id=contrat_id, locataire_id=locataire_id).first()

    if not contrat:
        return jsonify({"message": "Contrat non trouvé ou non autorisé."}), 404

    chambre = contrat.chambre
    maison = chambre.maison if chambre else None

    contrat_details = {
        "id": contrat.id,
        "chambre_id": chambre.id if chambre else None,
        "chambre_titre": chambre.titre if chambre else None,
        "chambre_description": chambre.description if chambre else None,
        "chambre_taille": chambre.taille if chambre else None,
        "chambre_type": chambre.type if chambre else None,
        "chambre_meublee": chambre.meublee if chambre else None,
        "chambre_salle_de_bain": chambre.salle_de_bain if chambre else None,
        "chambre_prix": float(chambre.prix) if chambre and chambre.prix else None,
        "chambre_disponible": chambre.disponible if chambre else None,
        "chambre_adresse": f"{maison.adresse}, {maison.ville}" if maison else None,
        "date_debut": contrat.date_debut.isoformat(),
        "date_fin": contrat.date_fin.isoformat(),
        "montant_caution": float(contrat.montant_caution) if contrat.montant_caution else None,
        "mois_caution": contrat.mois_caution,
        "mode_paiement": contrat.mode_paiement,
        "periodicite": contrat.periodicite,
        "statut": contrat.statut,
        "description": contrat.description,
        "cree_le": contrat.cree_le.isoformat(),
        "paiements": [
            {"id": p.id, "montant": float(p.montant), "date_echeance": p.date_echeance.isoformat(), "statut": p.statut,
             "description": p.description} for p in contrat.paiements]
    }
    return jsonify(contrat_details), 200


@locataire_bp.route('/contrats/<int:contrat_id>/paiements', methods=['GET'])
@jwt_required()
def get_locataire_contrat_paiements(contrat_id):
    current_user_identity = get_jwt_identity()
    locataire_id = json.loads(current_user_identity)['id']

    contrat = Contrat.query.filter_by(id=contrat_id, locataire_id=locataire_id).first()
    if not contrat:
        return jsonify({"message": "Contrat non trouvé ou non autorisé."}), 404

    paiements = Paiement.query.filter_by(contrat_id=contrat_id).order_by(Paiement.date_echeance.asc()).all()

    results = []
    for paiement in paiements:
        results.append({
            "id": paiement.id,
            "montant": float(paiement.montant),
            "date_echeance": paiement.date_echeance.isoformat(),
            "date_paiement": paiement.date_paiement.isoformat() if paiement.date_paiement else None,
            "statut": paiement.statut,
            "description": paiement.description if hasattr(paiement, 'description') else None,
            # Added description field
            "cree_le": paiement.cree_le.isoformat()
        })
    return jsonify(results), 200

# REMOVE THESE ROUTES AS DemandeLocation DOES NOT EXIST
# @locataire_bp.route('/demander-location', methods=['POST'])
# @jwt_required()
# def creer_demande_location():
#     pass # ... (delete the entire function) ...

# @locataire_bp.route('/demandes-location', methods=['GET'])
# @jwt_required()
# def get_mes_demandes_location():
#     pass # ... (delete the entire function) ...