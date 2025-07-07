from datetime import datetime

from flask import Blueprint, request, jsonify, abort

from app import db
from app.models import Utilisateur, Chambre, RendezVous
from app.serialisation import serialize_rendez_vous

rendez_vous_bp = Blueprint('rendez_vous_bp', __name__, url_prefix='/api')


# --- CRUD pour les Rendez-vous (User Story 8) ---

@rendez_vous_bp.route('/rendezvous', methods=['POST'])
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


@rendez_vous_bp.route('/rendezvous', methods=['GET'])
def get_rendezvous():
    rendezvous = RendezVous.query.all()
    return jsonify([serialize_rendez_vous(r) for r in rendezvous]), 200


@rendez_vous_bp.route('/rendezvous/<int:rendezvous_id>', methods=['GET'])
def get_single_rendezvous(rendezvous_id):
    rendezvous = RendezVous.query.get_or_404(rendezvous_id)
    return jsonify(serialize_rendez_vous(rendezvous)), 200


@rendez_vous_bp.route('/rendezvous/<int:rendezvous_id>', methods=['PUT'])
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


@rendez_vous_bp.route('/rendezvous/<int:rendezvous_id>', methods=['DELETE'])
def delete_rendezvous(rendezvous_id):
    rendezvous = RendezVous.query.get_or_404(rendezvous_id)
    db.session.delete(rendezvous)
    db.session.commit()
    return jsonify(message="Rendez-vous supprimé avec succès"), 204
