import hashlib
import json
import random
import uuid
from datetime import timedelta, datetime, date

import paydunya
from dateutil.relativedelta import relativedelta
from flask import Blueprint, request, jsonify, current_app, redirect
from flask_jwt_extended import jwt_required, get_jwt_identity
from paydunya import Store, InvoiceItem
from sqlalchemy.orm import joinedload, selectinload  # Import joinedload here

from app import db
from app.models import Chambre, Maison, Contrat, Utilisateur, Paiement
from app.serialization import serialize_media  # Add others if needed for other routes

locataire_bp = Blueprint('locataire', __name__, url_prefix='/api/locataire')


def get_current_locataire():
    current_user_identity = get_jwt_identity()
    locataire_id = json.loads(current_user_identity)['id']
    return locataire_id


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
    locataire_id = get_current_locataire()
    locataire = Utilisateur.query.get(locataire_id)

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
    locataire_id = get_current_locataire()

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
    locataire_id = get_current_locataire()

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
    locataire_id = get_current_locataire()

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


@locataire_bp.route('/mes-contrats', methods=['GET'])  # Nouvelle route
@jwt_required()
def get_mes_contrats():  # Fonction renommée
    locataire_id = get_current_locataire()
    locataire = Utilisateur.query.get(locataire_id)

    if not locataire or locataire.role != 'locataire':
        return jsonify({"message": "Accès refusé. Seuls les locataires peuvent voir leurs contrats."}), 403

    # Charger tous les contrats SAUF ceux en attente de validation
    contrats = Contrat.query.options(
        joinedload(Contrat.chambre).joinedload(Chambre.maison).joinedload(Maison.proprietaire)
    ).filter(
        Contrat.locataire_id == locataire.id,
        Contrat.statut.in_(['actif', 'rejete', 'termine', 'resilie'])  # Exclure explicitement 'en_attente_validation'
    ).order_by(Contrat.date_debut.desc()).all()  # Tri par date la plus récente

    results = []
    for contrat in contrats:
        proprietaire_nom = 'N/A'
        if contrat.chambre and contrat.chambre.maison and contrat.chambre.maison.proprietaire:
            proprietaire_nom = contrat.chambre.maison.proprietaire.nom_utilisateur

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


@locataire_bp.route('/mes-demandes-en-attente', methods=['GET'])
@jwt_required()
def get_mes_demandes_en_attente():
    locataire_id = get_current_locataire()
    locataire = Utilisateur.query.get(locataire_id)

    if not locataire or locataire.role != 'locataire':
        return jsonify({"message": "Accès refusé. Seuls les locataires peuvent voir leurs demandes."}), 403

    demandes = Contrat.query.options(
        joinedload(Contrat.chambre).joinedload(Chambre.maison).joinedload(Maison.proprietaire)
    ).filter(
        Contrat.locataire_id == locataire.id,
        Contrat.statut == 'en_attente_validation'  # Filtrer spécifiquement les demandes en attente
    ).order_by(Contrat.cree_le.desc()).all()  # Tri par date de création la plus récente

    results = []
    for contrat in demandes:
        proprietaire_nom = 'N/A'
        if contrat.chambre and contrat.chambre.maison and contrat.chambre.maison.proprietaire:
            proprietaire_nom = contrat.chambre.maison.proprietaire.nom_utilisateur

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


@locataire_bp.route('/mes-paiements', methods=['GET'])
@jwt_required()
def get_mes_paiements():
    current_user_id = get_current_locataire()
    locataire = Utilisateur.query.get(current_user_id)

    if not locataire or locataire.role != 'locataire':
        return jsonify({"message": "Accès refusé. Seuls les locataires peuvent voir leurs paiements."}), 403

    # Récupérer tous les contrats du locataire, avec leurs paiements et les détails de la chambre/propriétaire
    # Utiliser selectinload pour les paiements est souvent plus efficace pour les relations one-to-many
    contrats = Contrat.query.options(
        joinedload(Contrat.chambre).joinedload(Chambre.maison).joinedload(Maison.proprietaire),
        selectinload(Contrat.paiements)  # Charger les paiements pour chaque contrat séparément
    ).filter(
        Contrat.locataire_id == locataire.id,
        Contrat.statut.in_(['actif', 'termine', 'resilie'])
    ).all()

    results = []
    for contrat in contrats:
        proprietaire_nom = contrat.chambre.maison.proprietaire.nom_utilisateur if contrat.chambre and contrat.chambre.maison and contrat.chambre.maison.proprietaire else 'N/A'

        # Trier les paiements du contrat DANS LA BOUCLE PYTHON
        # Convertir en liste pour s'assurer que .sort() fonctionne (si ce n'est pas déjà une liste mutable)
        sorted_paiements = sorted(contrat.paiements, key=lambda p: p.date_echeance)

        paiements_data = []
        for paiement in sorted_paiements:  # Utiliser la liste triée
            paiements_data.append({
                "id": paiement.id,
                "montant": paiement.montant,
                "date_echeance": paiement.date_echeance.isoformat(),
                "date_paiement": paiement.date_paiement.isoformat() if paiement.date_paiement else None,
                "statut": paiement.statut,
            })

        results.append({
            "contrat_id": contrat.id,
            "chambre_titre": contrat.chambre.titre if contrat.chambre else 'N/A',
            "chambre_adresse": contrat.chambre.maison.adresse if contrat.chambre and contrat.chambre.maison else 'N/A',
            "proprietaire_nom": proprietaire_nom,
            "statut_contrat": contrat.statut,
            "date_debut_contrat": contrat.date_debut.isoformat(),
            "date_fin_contrat": contrat.date_fin.isoformat(),
            "paiements": paiements_data
        })
    return jsonify(results), 200


@locataire_bp.route('/paiements/<int:paiement_id>/marquer-paye', methods=['PUT'])
@jwt_required()
def marquer_paiement_paye(paiement_id):
    current_user_id = get_current_locataire()
    locataire = Utilisateur.query.get(current_user_id)

    if not locataire or locataire.role != 'locataire':
        return jsonify({"message": "Accès refusé."}), 403

    paiement = Paiement.query.options(
        joinedload(Paiement.contrat)  # Charger le contrat associé pour vérifier que le locataire est le bon
    ).filter(
        Paiement.id == paiement_id,
        Paiement.contrat.has(locataire_id=locataire.id)
        # Vérifier que ce paiement appartient bien à un contrat du locataire authentifié
    ).first()

    if not paiement:
        return jsonify({"message": "Paiement non trouvé ou vous n'êtes pas autorisé à modifier ce paiement."}), 404

    if paiement.statut == 'paye':
        return jsonify({"message": "Ce paiement est déjà marqué comme payé."}), 400

    try:
        paiement.statut = 'paye'
        paiement.date_paiement = date.today()  # Enregistrer la date du paiement
        db.session.add(paiement)
        db.session.commit()
        return jsonify({"message": "Paiement marqué comme payé avec succès."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Erreur lors du marquage du paiement: {str(e)}"}), 500


@locataire_bp.route('/mes-chambres', methods=['GET'])
@jwt_required()
def get_mes_chambres():
    current_user_id = get_current_locataire()
    locataire = Utilisateur.query.get(current_user_id)

    if not locataire or locataire.role != 'locataire':
        return jsonify({"message": "Accès refusé. Seuls les locataires peuvent voir leurs chambres associées."}), 403

    contrats_locataire = Contrat.query.options(
        joinedload(Contrat.chambre).joinedload(Chambre.maison)
    ).filter(
        Contrat.locataire_id == locataire.id,
        Contrat.statut.in_(['actif', 'termine', 'resilie'])  # Exclure les demandes en attente ou rejetées
    ).all()

    chambres_uniques = {}  # Utiliser un dictionnaire pour stocker les chambres uniques par leur ID
    for contrat in contrats_locataire:
        if contrat.chambre and contrat.chambre.id not in chambres_uniques:
            chambre = contrat.chambre
            maison = chambre.maison

            chambres_uniques[chambre.id] = {
                "id": chambre.id,
                "titre": chambre.titre,
                "description": chambre.description,
                "prix": chambre.prix,
                "disponible": chambre.disponible,
                "cree_le": chambre.cree_le.isoformat(),
                "maison": {
                    "id": maison.id,
                    "adresse": maison.adresse,
                    "ville": maison.ville,
                    "description": maison.description,
                    "proprietaire_id": maison.proprietaire_id
                } if maison else None
                # Vous pouvez ajouter d'autres champs de chambre si nécessaire
            }

    # Convertir le dictionnaire en liste de valeurs
    results = list(chambres_uniques.values())

    return jsonify(results), 200


@locataire_bp.route('/paiements/<int:paiement_id>/initier-paydunya', methods=['POST'])
@jwt_required()
def initier_paydunya_payment(paiement_id):
    current_user_id = get_current_locataire()
    locataire = Utilisateur.query.get(current_user_id)

    if not locataire or locataire.role != 'locataire':
        return jsonify({"message": "Accès refusé."}), 403

    paiement = Paiement.query.options(
        joinedload(Paiement.contrat).joinedload(Contrat.chambre)
    ).filter(
        Paiement.id == paiement_id,
        Paiement.contrat.has(locataire_id=locataire.id)
    ).first()

    if not paiement:
        return jsonify({"message": "Paiement non trouvé ou vous n'êtes pas autorisé."}), 404

    if paiement.statut in ['paye', 'en_cours_traitement']:
        return jsonify({"message": "Ce paiement est déjà effectué ou en cours de traitement."}), 400

    # Aucun besoin de 'phone_number' ou 'operator' ici pour l'initialisation PAR (Payment Avec Redirection)
    # L'utilisateur choisira son moyen de paiement sur la page PayDunya.
    # Les canaux peuvent être ajoutés pour filtrer les options si désiré, mais ne sont pas obligatoires.

    try:
        # 1. Configuration des informations du Store
        store_info = {
            "name": "Social Logement",
            "tagline": "Facilitez vos paiements de loyer",
            "phone_number": "771234567",  # Exemple, à remplacer par le numéro de votre entreprise
            "email": "contact@sociallogement.com",  # Exemple
            # Vous pouvez ajouter "website_url" et "logo_url" si vous les avez
        }
        store = Store(**store_info)

        # 3. Ajout des articles à la facture
        item_data = InvoiceItem(
            name=f"Loyer pour {paiement.contrat.chambre.titre}",
            quantity=1,
            unit_price=float(paiement.montant),
            total_price=float(paiement.montant),  # total_price doit être le produit de quantity * unit_price
            description=f"Paiement de loyer pour le contrat {paiement.contrat_id}"
        )

        # 2. Création de l'objet Invoice
        invoice = paydunya.Invoice(store)

        invoice.add_items([item_data])

        # 4. Configuration du montant total de la facture
        # Ce montant doit correspondre à la somme des total_price des items
        invoice.total_amount = float(paiement.montant) * item_data.quantity

        # 5. Ajout de la description générale de la facture (facultatif)
        invoice.description = f"Paiement de loyer pour le contrat {paiement.contrat_id} - Échéance {paiement.date_echeance.isoformat()}"

        # 6. Ajout de données supplémentaires (custom_data)
        invoice.add_custom_data({
            "paiement_id": paiement.id,
            "locataire_id": locataire.id,
            "contrat_id": paiement.contrat.id
        })

        # 7. Configuration des URLs de retour et de callback
        invoice.callback_url = current_app.config['PAYDUNYA_CALLBACK_URL']
        invoice.return_url = current_app.config['PAYDUNYA_RETURN_URL']
        invoice.cancel_url = current_app.config['PAYDUNYA_CANCEL_URL']

        # 8. Ajouter des canaux spécifiques si vous voulez restreindre les options (facultatif)
        invoice.add_channel('orange-money-senegal')
        invoice.add_channel('wave-senegal')

        success, paydunya_api_response = invoice.create()

        if success:

            paydunya_token = paydunya_api_response.get('token')
            payment_page_url = paydunya_api_response.get('response_text')

            if not paydunya_token or not payment_page_url:
                print(
                    f"DEBUG: Token ou URL de paiement manquant dans la réponse PayDunya: {json.dumps(paydunya_api_response, indent=2)}")
                return jsonify({
                    "message": "Erreur: Token ou URL de paiement non reçu de PayDunya.",
                    "status": "failed",
                    "error_details": "Token or checkout_url is missing in PayDunya API response."
                }), 400

            # Mettre à jour le statut du paiement et sauvegarder le token PayDunya
            paiement.statut = 'en_cours_traitement'
            paiement.paydunya_invoice_token = paydunya_token
            db.session.add(paiement)
            db.session.commit()

            # Retourner l'URL de redirection au frontend
            return jsonify({
                "message": "Paiement initié avec succès. Redirection vers PayDunya.",
                "paydunya_invoice_token": paydunya_token,
                "status": "initiated",
                "redirect_url": payment_page_url  # Cette URL doit être fournie au frontend
            }), 200
        else:
            # En cas d'échec de la création de la facture par PayDunya
            error_message = paydunya_api_response.get('response_text', "Erreur inconnue.")
            response_code = paydunya_api_response.get('response_code', "N/A")
            print(f"PayDunya Invoice Creation Failed: {error_message} - Response Code: {response_code}")
            return jsonify({
                "message": f"Échec de l'initialisation PayDunya: {error_message}",
                "status": "failed",
                "error_details": error_message
            }), 400

    except Exception as e:
        db.session.rollback()
        print(f"Erreur interne lors de l'initialisation du paiement PayDunya: {str(e)}")
        return jsonify(
            {"message": f"Erreur interne lors de l'initialisation du paiement: {str(e)}", "status": "failed"}), 500


@locataire_bp.route('/paydunya/callback', methods=['POST'])
def paydunya_callback():
    data = {}
    for key, value in request.form.items():
        parts = key.split('[')
        current_dict = data
        for i, part in enumerate(parts):
            part = part.replace(']', '')  # Clean up ']' from part
            if i == len(parts) - 1:
                current_dict[part] = value
            else:
                if part not in current_dict:
                    current_dict[part] = {}
                current_dict = current_dict[part]

    print(f"DEBUG: Reconstructed Callback Data: {json.dumps(data, indent=2)}")

    received_hash = data.get('data', {}).get('hash')
    invoice_token = data.get('data', {}).get('invoice', {}).get('token')
    status = data.get('data', {}).get('status')
    transaction_id = data.get('data', {}).get('invoice', {}).get('transaction_id')

    if not received_hash:
        print("Missing 'data[hash]' in PayDunya callback data (from request.form).")
        return jsonify({"message": "Missing hash in callback"}), 400

    if not invoice_token:
        print("Missing 'data[invoice][token]' in PayDunya callback data (from request.form).")
        return jsonify({"message": "Missing invoice token"}), 400

    master_key = current_app.config['PAYDUNYA_MASTER_KEY']

    try:
        data_for_hashing = {}
        for key, value in request.form.items():
            if key.startswith('data[') and key != 'data[hash]':
                data_for_hashing[key] = value

        parsed_data = {}
        for key, value in request.form.items():
            parts = key.split('[')
            current = parsed_data
            for i, part in enumerate(parts):
                part = part.replace(']', '')
                if i == len(parts) - 1:
                    current[part] = value
                else:
                    if part not in current:
                        current[part] = {}
                    current = current[part]

        data_to_hash_dict = parsed_data.get('data', {}).copy()
        if 'hash' in data_to_hash_dict:
            del data_to_hash_dict['hash']

        expected_hash = hashlib.sha512(master_key.encode('utf-8')).hexdigest()

        if expected_hash != received_hash:
            print(f"Hash mismatch! Expected: {expected_hash}, Received: {received_hash}")
            return jsonify({"message": "Invalid Hash Signature"}), 403

        # If the hash is valid, proceed with payment processing
        paiement = Paiement.query.filter_by(paydunya_invoice_token=invoice_token).first()

        if not paiement:
            print(f"Callback received for unknown invoice token: {invoice_token}")
            return jsonify({"message": "Payment not found"}), 404

        # Update payment status
        if status == 'completed':
            if paiement.statut != 'paye':
                paiement.statut = 'paye'
                paiement.date_paiement = datetime.now().date()
                paiement.paydunya_transaction_id = transaction_id
                db.session.add(paiement)
                db.session.commit()
                print(f"Paiement {paiement.id} for invoice {invoice_token} marked as paid.")
            return jsonify({"message": "Payment updated to completed"}), 200
        elif status == 'pending':
            print(f"Paiement {paiement.id} for invoice {invoice_token} is still pending.")
            if paiement.statut not in ['en_cours_traitement', 'pending_paydunya_status']:
                paiement.statut = 'en_cours_traitement'
                db.session.add(paiement)
                db.session.commit()
            return jsonify({"message": "Payment still pending"}), 200
        elif status in ['cancelled', 'failed', 'expired']:
            if paiement.statut != 'impaye':
                paiement.statut = 'impaye'
                paiement.paydunya_transaction_id = None
                db.session.add(paiement)
                db.session.commit()
                print(f"Paiement {paiement.id} for invoice {invoice_token} marked as {status}.")
            return jsonify({"message": f"Payment updated to {status}"}), 200
        else:
            print(f"Unknown status received for invoice {invoice_token}: {status}")
            return jsonify({"message": "Unknown status"}), 400

    except Exception as e:
        db.session.rollback()
        print(f"Error processing PayDunya callback for invoice {invoice_token}: {str(e)}")
        print(f"Full callback request data (from request.form): {request.form}")  # Log request.form for debugging
        return jsonify({"message": f"Internal server error: {str(e)}"}), 500


@locataire_bp.route('/mes-paiements/success', methods=['GET'])
def paiement_succes():
    paydunya_token = request.args.get('token')

    if not paydunya_token:
        print("Token de paiement manquant sur la page de succès.")
        return redirect("http://localhost:5173/lodger/dashboard/paiements?status=error&message=token_missing")

    invoice = paydunya.Invoice()  # Instanciation de l'objet Invoice
    print(f"DEBUG: Invoice: {invoice}")
    successful, response = invoice.confirm(paydunya_token)
    print(f"DEBUG: Response: {json.dumps(response, indent=2)}")
    try:
        if successful and response['status'] == "completed":
            print(f"Paiement {paydunya_token} confirmé avec succès via return_url.")
            return redirect(f"http://localhost:5173/lodger/dashboard/paiements?token={paydunya_token}&status=success")
        else:
            status_paydunya = response.status if response else "unknown"
            print(f"Paiement {paydunya_token} non confirmé comme complété. Statut PayDunya: {status_paydunya}")
            return redirect(
                f"http://localhost:5173/lodger/dashboard/paiements?token={paydunya_token}&status={status_paydunya}&message=payment_not_completed")

    except Exception as e:
        print(f"Erreur lors de la vérification du statut PayDunya via return_url: {e}")
        return redirect(
            f"http://localhost:5173/lodger/dashboard/paiements?token={paydunya_token}&status=error&message=internal_verification_error")


@locataire_bp.route('/mes-paiements/cancel', methods=['GET'])
def paiement_cancel():
    paydunya_token = request.args.get('token')

    if not paydunya_token:
        print("Token de paiement manquant sur la page d'annulation.")
        return redirect("http://localhost:5173/lodger/dashboard/paiements?status=error&message=token_missing")

    try:
        invoice = paydunya.Invoice()  # Instanciation de l'objet Invoice
        successful, response = invoice.confirm(paydunya_token)
        status_paydunya = response.status if response else "unknown"

        print(f"Paiement {paydunya_token} annulé/échoué via cancel_url. Statut PayDunya: {status_paydunya}")
        return redirect(
            f"http://localhost:5173/lodger/dashboard/paiements?token={paydunya_token}&status={status_paydunya}&message=payment_cancelled_or_failed")

    except Exception as e:
        print(f"Erreur lors de la vérification du statut PayDunya via cancel_url: {e}")
        return redirect(
            f"http://localhost:5173/lodger/dashboard/paiements?token={paydunya_token}&status=error&message=internal_verification_error")
