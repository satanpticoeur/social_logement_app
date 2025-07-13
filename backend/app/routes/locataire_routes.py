from datetime import timedelta, datetime, date

from dateutil.relativedelta import relativedelta
from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models import Chambre, Maison, Contrat, Utilisateur, Paiement
from flask_jwt_extended import jwt_required, get_jwt_identity
import json
from sqlalchemy.orm import joinedload  # Import joinedload here

from app.serialization import serialize_media  # Add others if needed for other routes

locataire_bp = Blueprint('locataire', __name__, url_prefix='/api/locataire')


@locataire_bp.route('/chambres/recherche', methods=['GET'])
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
def soumettre_demande_location(chambre_id):
    current_user_identity = get_jwt_identity()
    current_user_id = json.loads(current_user_identity)['id']
    locataire = Utilisateur.query.get(current_user_id)

    if not locataire or locataire.role != 'locataire':
        return jsonify({"message": "Accès refusé. Seuls les locataires peuvent soumettre des demandes."}), 403

    chambre = Chambre.query.get(chambre_id)
    if not chambre:
        return jsonify({"message": "Chambre non trouvée."}), 404

    contrat_existant_ou_attente = Contrat.query.filter(
        Contrat.chambre_id == chambre_id,
        Contrat.statut.in_(['actif', 'en_attente_validation'])
    ).first()

    if contrat_existant_ou_attente:
        return jsonify({"message": "Cette chambre a déjà une demande de location en attente ou un contrat actif."}), 400

    data = request.get_json()
    if not data:
        return jsonify({"message": "Données de requête manquantes."}), 400

    try:
        date_debut_str = data.get('date_debut')
        duree_mois = data.get('duree_mois')

        if not date_debut_str or not duree_mois:
            return jsonify({"message": "Les champs 'date_debut' et 'duree_mois' sont requis."}), 400

        date_debut = datetime.strptime(date_debut_str, '%Y-%m-%d').date()
        date_fin = date_debut + relativedelta(months=+duree_mois)

        if date_debut < datetime.now().date():
             return jsonify({"message": "La date de début ne peut pas être dans le passé."}), 400

    except ValueError:
        return jsonify({"message": "Format de date invalide. Utilisez YYYY-MM-DD."}), 400
    except Exception as e:
        return jsonify({"message": f"Erreur de validation des données: {str(e)}"}), 400

    try:
        loyer_mensuel = chambre.prix
        mois_caution = 1  # Par défaut, la caution est d'un mois de loyer
        montant_caution_calcule = loyer_mensuel * mois_caution

        nouveau_contrat = Contrat(
            locataire_id=locataire.id,
            chambre_id=chambre.id,
            date_debut=date_debut,
            date_fin=date_fin,
            montant_caution=montant_caution_calcule,
            mois_caution=mois_caution,
            duree_mois=duree_mois,
            description=f"Demande de location pour la chambre {chambre.titre}",
            mode_paiement="Virement Bancaire",
            periodicite="Mensuel",
            statut="en_attente_validation"
        )
        db.session.add(nouveau_contrat)
        db.session.commit()

        return jsonify({
            "message": f"Demande de location soumise avec succès. Montant de la caution estimé: {montant_caution_calcule} FCFA. En attente de validation par le propriétaire.",
            "contrat_id": nouveau_contrat.id
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Une erreur est survenue lors de la soumission de la demande: {str(e)}"}), 500




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

@locataire_bp.route('/mes-demandes-contrats', methods=['GET'])
@jwt_required()
def get_mes_demandes_contrats():
    current_user_identity = get_jwt_identity()
    locataire_id = json.loads(current_user_identity)['id']
    locataire = Utilisateur.query.get(locataire_id)

    if not locataire or locataire.role != 'locataire':
        return jsonify({"message": "Accès refusé. Seuls les locataires peuvent voir leurs demandes."}), 403

    # Charger tous les contrats (actifs, en attente, rejetés, terminés) pour ce locataire
    demandes_et_contrats = Contrat.query.options(
        joinedload(Contrat.chambre).joinedload(Chambre.maison).joinedload(Maison.proprietaire)
    ).filter(
        Contrat.locataire_id == locataire.id
    ).order_by(Contrat.date_debut.desc()).all() # Tri par date la plus récente

    results = []
    for contrat in demandes_et_contrats:
        proprietaire_nom = 'N/A'
        if contrat.chambre and contrat.chambre.maison and contrat.chambre.maison.proprietaire:
            proprietaire_nom = contrat.chambre.maison.proprietaire.nom_utilisateur  # Ou le champ approprié du nom d'utilisateur
        results.append({
            "id": contrat.id,
            "chambre_id": contrat.chambre.id,
            "chambre_titre": contrat.chambre.titre,
            "proprietaire_nom": proprietaire_nom,
            "date_debut": contrat.date_debut.isoformat(),
            "date_fin": contrat.date_fin.isoformat(),
            "montant_caution": contrat.montant_caution,
            "duree_mois": contrat.duree_mois,
            "statut": contrat.statut
        })
    return jsonify(results), 200



