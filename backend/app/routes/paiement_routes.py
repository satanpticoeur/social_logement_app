from flask import Blueprint, request, jsonify, abort
from datetime import datetime
from decimal import Decimal


from app import db
from app.models import Contrat, Paiement
from app.models import Maison, Chambre
from app.serialisation import  serialize_paiement

paiement_bp = Blueprint('paiement_bp', __name__, url_prefix='/api')

# --- CRUD pour les Paiements (User Story 3 & 4) ---

@paiement_bp.route('/paiements', methods=['POST'])
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


@paiement_bp.route('/paiements', methods=['GET'])
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


@paiement_bp.route('/paiements/<int:paiement_id>', methods=['GET'])
def get_paiement(paiement_id):
    paiement = Paiement.query.get_or_404(paiement_id)
    return jsonify(serialize_paiement(paiement)), 200


@paiement_bp.route('/paiements/<int:paiement_id>', methods=['PUT'])
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


@paiement_bp.route('/paiements/<int:paiement_id>', methods=['DELETE'])
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


@paiement_bp.route('/contrats/<int:contrat_id>/paiements', methods=['GET'])
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
