from flask import Blueprint, request, jsonify, abort
from flask_jwt_extended import get_jwt_identity

from app import db
from app.decorators import role_required
from app.models import Maison, Utilisateur
from app.serialisation import serialize_maison
import json

maison_bp = Blueprint('api', __name__, url_prefix='/api')


# --- CRUD pour les Maisons (restent les mêmes, mais la sérialisation est améliorée) ---

@maison_bp.route('/maisons', methods=['POST'])
@role_required(roles=['proprietaire'])
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


@maison_bp.route('/maisons', methods=['GET'])
@role_required(roles=['proprietaire', 'admin', 'locataire'])
def get_maisons():
    maisons = Maison.query.all()
    return jsonify([serialize_maison(m) for m in maisons]), 200


@maison_bp.route('/maisons/<int:maison_id>', methods=['GET'])
@role_required(roles=['proprietaire', 'admin', 'locataire'])
def get_maison(maison_id):
    # Charger la maison et son propriétaire pour la sérialisation
    maison = Maison.query.options(db.joinedload(Maison.proprietaire)).get_or_404(maison_id)
    return jsonify(serialize_maison(maison)), 200


@maison_bp.route('/maisons/<int:maison_id>', methods=['PUT'])
@role_required(roles=['proprietaire'])
def update_maison(maison_id):
    current_user_identity = get_jwt_identity()
    current_user_id = json.loads(current_user_identity)['id']
    data = request.get_json()
    if not data:
        return jsonify({"message": "Données JSON requises"}), 400

    # 3. Validation des données d'entrée
    # Ajoutez ici des validations plus robustes (taille, type, etc.)
    adresse = data.get('adresse')
    ville = data.get('ville')
    description = data.get('description', None)  # La description peut être null

    if not adresse or not ville:
        return jsonify({"message": "L'adresse et la ville sont requises"}), 400

    # maison = Maison.query.get(maison_id)

    # charger maison avec propriétaire
    maison = Maison.query.options(db.joinedload(Maison.proprietaire)).get(maison_id)


    if not maison:
        return jsonify({"message": "Maison non trouvée"}), 404

    if maison.proprietaire_id != current_user_id:  # Supposons que Maison ait un champ proprietaire_id
        return jsonify({"message": "Vous n'êtes pas autorisé à modifier cette maison"}), 403

    # 6. Mise à jour des champs de la maison
    maison.adresse = adresse
    maison.ville = ville
    maison.description = description
    # Mettez à jour d'autres champs si nécessaire, par exemple:
    # maison.nombre_chambres = data.get('nombre_chambres', maison.nombre_chambres)

    try:
        db.session.commit()
        return jsonify({"message": "Maison mise à jour avec succès", "maison": {
            "id": maison.id,
            "adresse": maison.adresse,
            "ville": maison.ville,
            "description": maison.description
        }}), 200  # ou return '', 204
    except Exception as e:
        db.session.rollback()
        print(f"Erreur lors de la mise à jour de la maison: {e}")
        return jsonify({"message": "Erreur interne du serveur lors de la mise à jour"}), 500


@maison_bp.route('/maisons/<int:maison_id>', methods=['DELETE'])
@role_required(roles=['proprietaire'])
def delete_maison(maison_id):
    maison = Maison.query.get_or_404(maison_id)
    db.session.delete(maison)
    db.session.commit()
    return jsonify(message="Maison supprimée avec succès"), 204
