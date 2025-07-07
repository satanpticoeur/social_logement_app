from datetime import timedelta, datetime, date

from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models import Chambre, Maison, Media, Contrat, Utilisateur, Paiement
from flask_jwt_extended import jwt_required, get_jwt_identity  # Si vous voulez que la recherche nécessite une connexion
import json
locataire_bp = Blueprint('locataire', __name__, url_prefix='/api/locataire')

# Note : Si vous voulez que cette route soit accessible sans authentification,
# retirez le décorateur @jwt_required()
@locataire_bp.route('/chambres/recherche', methods=['GET'])
# @jwt_required() # Décommentez si la recherche est réservée aux utilisateurs connectés
def search_chambres():
    # Récupérer les paramètres de requête (query parameters)
    ville = request.args.get('ville')
    min_prix = request.args.get('min_prix', type=float)
    max_prix = request.args.get('max_prix', type=float)
    type_chambre = request.args.get('type')
    meublee = request.args.get('meublee')
    disponible = request.args.get('disponible', type=bool, default=True) # Par défaut, ne montrer que les disponibles
    query = Chambre.query.join(Maison) # Joindre avec Maison pour filtrer par ville, etc.

    # Appliquer les filtres
    if ville:
        query = query.filter(Maison.ville.ilike(f'%{ville}%')) # Recherche insensible à la casse
    if min_prix is not None:
        query = query.filter(Chambre.prix >= min_prix)
    if max_prix is not None:
        query = query.filter(Chambre.prix <= max_prix)
    if type_chambre:
        query = query.filter(Chambre.type.ilike(f'%{type_chambre}%'))
    if meublee is not None: # Vérifier si meublee est un booléen
        print(f"Valeur de meublee reçue : {meublee}")  # Pour débogage
        if meublee == 'false':
            meublee = False
        else:
            meublee = True
        query = query.filter(Chambre.meublee == meublee)
    if disponible is not None: # Ceci est important pour les locataires
        query = query.filter(Chambre.disponible == disponible)

    chambres = query.all()

    results = []
    for chambre in chambres:
        # Récupérer les médias (photos) pour chaque chambre
        medias_data = [
            {"id": media.id, "url": media.url, "type": media.type, "description": media.description}
            for media in chambre.medias
        ]

        # Inclure l'adresse de la maison pour faciliter la recherche front-end
        results.append({
            "id": chambre.id,
            "maison_id": chambre.maison_id,
            "adresse_maison": chambre.maison.adresse,
            "ville_maison": chambre.maison.ville,
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
# @jwt_required() # Décommentez si les détails de chambre sont réservés aux utilisateurs connectés
def get_chambre_details(chambre_id):
    chambre = Chambre.query.get(chambre_id)

    if not chambre or not chambre.disponible: # S'assurer que la chambre est disponible pour les locataires
        return jsonify({"message": "Chambre non trouvée ou non disponible."}), 404

    medias_data = [
        {"id": media.id, "url": media.url, "type": media.type, "description": media.description}
        for media in chambre.medias
    ]

    return jsonify({
        "id": chambre.id,
        "maison_id": chambre.maison_id,
        "adresse_maison": chambre.maison.adresse,
        "ville_maison": chambre.maison.ville,
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

# Fonction utilitaire pour générer les paiements (peut être placée ici ou dans un fichier utils.py)
def generer_paiements_contrat(contrat: Contrat):
    """
    Génère les paiements mensuels pour un contrat donné.
    """
    paiements_generes = []
    current_date = contrat.date_debut
    # Le prix de la chambre est le montant du loyer mensuel
    loyer_mensuel = contrat.chambre.prix

    # Gérer la caution si elle existe et n'est pas déjà un paiement
    if contrat.montant_caution and contrat.montant_caution > 0:
        # Pour le MVP, on suppose que la caution est due à la date de début du contrat
        paiement_caution = Paiement(
            contrat_id=contrat.id,
            montant=contrat.montant_caution,
            date_echeance=contrat.date_debut,
            statut='impayé', # Initialement impayé, le locataire devra le "payer"
            description="Paiement de la caution"
        )
        db.session.add(paiement_caution)
        paiements_generes.append(paiement_caution)

    # Générer les paiements mensuels
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

        # Passer au mois suivant
        # Gérer le changement d'année et de mois correctement
        year = current_date.year
        month = current_date.month + 1
        if month > 12:
            month = 1
            year += 1
        # Essayer de garder le même jour du mois, sinon, le dernier jour du mois
        try:
            current_date = date(year, month, current_date.day)
        except ValueError: # Si le jour n'existe pas dans le mois (ex: 31 Février)
            current_date = date(year, month, 1) + timedelta(days=-1) # Dernier jour du mois précédent

    return paiements_generes


@locataire_bp.route('/chambres/<int:chambre_id>/louer', methods=['POST'])
@jwt_required()
def louer_chambre(chambre_id):
    current_user_identity = get_jwt_identity()
    locataire_id = json.loads(current_user_identity)['id']

    locataire = Utilisateur.query.get(locataire_id)
    if not locataire or locataire.role != 'locataire': # Vérifier le rôle de l'utilisateur
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

    # Calcul de la date de fin : duree_mois est le nombre de mois complets
    # Par exemple, pour 12 mois, du 1er Janvier au 31 Décembre de la même année.
    # Pour simplifier, nous allons juste ajouter les mois.
    # Une meilleure approche serait d'utiliser dateutil.relativedelta
    # Pour un MVP, on peut faire une estimation simple :
    # Si le contrat commence le 1er janvier et dure 12 mois, il se termine le 31 décembre.
    # Si le contrat commence le 15 janvier et dure 12 mois, il se termine le 14 janvier de l'année suivante.
    date_fin_contrat = date_debut_contrat
    for _ in range(duree_mois):
        year, month = date_fin_contrat.year, date_fin_contrat.month
        month += 1
        if month > 12:
            month = 1
            year += 1
        try:
            date_fin_contrat = date(year, month, date_fin_contrat.day)
        except ValueError: # Pour gérer les mois avec moins de jours (ex: février)
            date_fin_contrat = date(year, month, 1) - timedelta(days=1) # Aller au dernier jour du mois précédent (ex: 28 ou 29 fév)

    # Assurez-vous que la date de fin est le jour avant pour une durée exacte de X mois
    date_fin_contrat = date_fin_contrat - timedelta(days=1)


    montant_caution = data.get('montant_caution', float(chambre.prix) * 2) # Par défaut 2 mois de loyer comme caution
    mois_caution = data.get('mois_caution', 2)
    mode_paiement = data.get('mode_paiement', 'virement_bancaire')
    periodicite = data.get('periodicite', 'mensuel')

    try:
        db.session.begin_nested() # Début de la transaction

        # 1. Mettre à jour la disponibilité de la chambre
        chambre.disponible = False
        db.session.add(chambre)

        # 2. Créer le contrat
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
        db.session.flush() # Permet d'obtenir l'ID du contrat avant le commit complet

        # 3. Générer les paiements pour ce contrat
        generer_paiements_contrat(new_contrat)

        db.session.commit() # Commit la transaction entière

        return jsonify({
            "message": "Chambre louée avec succès et contrat, incluant l'échéancier des paiements, généré !",
            "chambre_id": chambre.id,
            "contrat_id": new_contrat.id,
            "chambre_disponible": chambre.disponible
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erreur lors de la location de la chambre {chambre_id} ou génération des paiements: {e}")
        return jsonify({"message": "Erreur lors de la location de la chambre. Veuillez réessayer.", "error": str(e)}), 500


@locataire_bp.route('/contrats', methods=['GET'])
@jwt_required()
def get_locataire_contrats():
    current_user_identity = get_jwt_identity()
    locataire_id = json.loads(current_user_identity)['id']

    # Récupérer tous les contrats où cet utilisateur est le locataire
    # Trier par date de début (les plus récents en premier)
    contrats = Contrat.query.filter_by(locataire_id=locataire_id).order_by(Contrat.date_debut.desc()).all()

    results = []
    for contrat in contrats:
        # Assurez-vous de charger la chambre et la maison pour les infos affichées
        chambre = contrat.chambre
        maison = chambre.maison

        results.append({
            "id": contrat.id,
            "chambre_id": chambre.id,
            "chambre_titre": chambre.titre,
            "chambre_adresse": f"{maison.adresse}, {maison.ville}",
            "prix_mensuel_chambre": float(chambre.prix), # Inclure le prix de la chambre
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

# Endpoint pour obtenir les détails d'un contrat spécifique du locataire (optionnel pour l'instant)
@locataire_bp.route('/contrats/<int:contrat_id>', methods=['GET'])
@jwt_required()
def get_locataire_contrat_details(contrat_id):
    current_user_identity = get_jwt_identity()
    locataire_id = json.loads(current_user_identity)['id']

    contrat = Contrat.query.filter_by(id=contrat_id, locataire_id=locataire_id).first()

    if not contrat:
        return jsonify({"message": "Contrat non trouvé ou non autorisé."}), 404

    chambre = contrat.chambre
    maison = chambre.maison

    contrat_details = {
        "id": contrat.id,
        "chambre_id": chambre.id,
        "chambre_titre": chambre.titre,
        "chambre_description": chambre.description,
        "chambre_taille": chambre.taille,
        "chambre_type": chambre.type,
        "chambre_meublee": chambre.meublee,
        "chambre_salle_de_bain": chambre.salle_de_bain,
        "chambre_prix": float(chambre.prix),
        "chambre_disponible": chambre.disponible,
        "chambre_adresse": f"{maison.adresse}, {maison.ville}",
        "date_debut": contrat.date_debut.isoformat(),
        "date_fin": contrat.date_fin.isoformat(),
        "montant_caution": float(contrat.montant_caution) if contrat.montant_caution else None,
        "mois_caution": contrat.mois_caution,
        "mode_paiement": contrat.mode_paiement,
        "periodicite": contrat.periodicite,
        "statut": contrat.statut,
        "description": contrat.description,
        "cree_le": contrat.cree_le.isoformat(),
        # Vous pouvez ajouter ici la liste des paiements associés si vous les avez déjà implémentés
        "paiements": [{"id": p.id, "montant": float(p.montant), "date_echeance": p.date_echeance.isoformat(), "statut": p.statut} for p in contrat.paiements]
    }
    return jsonify(contrat_details), 200


# your_app_name/locataire_routes.py
# ... (imports existants) ...
# ... (vos routes existantes) ...

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
            "description": paiement.description,
            "cree_le": paiement.cree_le.isoformat()
        })
    return jsonify(results), 200