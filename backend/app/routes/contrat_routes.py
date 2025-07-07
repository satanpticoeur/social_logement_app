
from flask import Blueprint, request, jsonify, abort
from app.models import Maison, Utilisateur, Chambre, Media

from app import db
from app.models import Contrat, Paiement
from datetime import date
from dateutil.relativedelta import relativedelta

from app.decorators import role_required
from app.routes.user_routes import serialize_utilisateur
from app.serialisation import serialize_contrat

contrat_bp = Blueprint('contrat_bp', __name__, url_prefix='/api')

# --- CRUD pour les Contrats (User Story 5) ---

@contrat_bp.route('/contrats', methods=['POST'])
@role_required(roles=['proprietaire'])
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


@contrat_bp.route('/contrats', methods=['GET'])
@role_required(roles=['proprietaire', 'locataire', 'admin'])
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


@contrat_bp.route('/contrats/<int:contrat_id>', methods=['GET'])
@role_required(roles=['proprietaire', 'locataire', 'admin'])
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


@contrat_bp.route('/contrats/<int:contrat_id>', methods=['PUT'])
@role_required(roles=['proprietaire'])
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


@contrat_bp.route('/contrats/<int:contrat_id>', methods=['DELETE'])
@role_required(roles=['proprietaire'])
def delete_contrat(contrat_id):
    contrat = Contrat.query.get_or_404(contrat_id)
    db.session.delete(contrat)
    db.session.commit()
    return jsonify(message="Contrat supprimé avec succès"), 204
