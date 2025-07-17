
from flask import Blueprint, request, jsonify, abort
from flask_jwt_extended import get_jwt_identity

from app.models import Maison, Chambre
from app import db
import json

from app.decorators import role_required
from app.routes.user_routes import serialize_utilisateur
from app.serialization import serialize_chambre

chambre_bp = Blueprint('chambre_bp', __name__, url_prefix='/api')


## --- CRUD pour les Chambres (restent les mêmes, mais la sérialisation est améliorée et filtrage pour user story 2 & 7) ---


@chambre_bp.route('/chambres', methods=['POST'])
@role_required(['proprietaire'])
def add_chambre():
    current_user_identity = get_jwt_identity()
    owner_id = json.loads(current_user_identity)['id']
    data = request.get_json()

    print(data)

    # Le champ 'prix' est maintenant requis
    required_fields = ['maison_id', 'titre', 'prix']
    for field in required_fields:
        if field not in data:
            return jsonify({"message": f"Le champ '{field}' est requis."}), 400

    maison = Maison.query.filter_by(id=data['maison_id'], proprietaire_id=owner_id).first()
    if not maison:
        return jsonify({"message": "Maison non trouvée ou ne vous appartient pas."}), 404

    try:
        # Utilise uniquement 'prix'
        chambre_prix = float(data['prix'])
    except ValueError:
        return jsonify({"message": "Le prix doit être un nombre valide."}), 400

    new_chambre = Chambre(
        maison_id=data['maison_id'],
        titre=data['titre'],
        description=data.get('description'),
        taille=data.get('taille'),
        type=data.get('type'),
        meublee=data.get('meublee', False),
        salle_de_bain=data.get('salle_de_bain', False),
        prix=chambre_prix,  # Utilisez le champ 'prix' unique
        disponible=data.get('disponible', True)
    )

    db.session.add(new_chambre)
    maison.nombre_chambres += 1
    db.session.commit()

    return jsonify({
        "message": "Chambre ajoutée avec succès.",
        "chambre": {
            "id": new_chambre.id,
            "maison_id": new_chambre.maison_id,
            "titre": new_chambre.titre,
            "description": new_chambre.description,
            "taille": new_chambre.taille,
            "type": new_chambre.type,
            "meublee": new_chambre.meublee,
            "salle_de_bain": new_chambre.salle_de_bain,
            "prix": float(new_chambre.prix),  # Assurez-vous que c'est un float pour le JSON
            "disponible": new_chambre.disponible
        }
    }), 201

@chambre_bp.route('/chambres', methods=['GET'])
def get_chambres():
    proprietaire_id = request.args.get('proprietaire_id', type=int)
    query = Chambre.query.options(db.joinedload(Chambre.maison).joinedload(Maison.proprietaire),
                                  db.joinedload(Chambre.medias))

    if proprietaire_id:
        # Filtrer les chambres qui appartiennent à une maison de ce propriétaire
        query = query.join(Maison).filter(Maison.proprietaire_id == proprietaire_id)

    chambres = query.all()
    return jsonify([serialize_chambre(c) for c in chambres]), 200


@chambre_bp.route('/chambres/<int:chambre_id>', methods=['GET'])
@role_required(roles=['proprietaire', 'admin', 'locataire'])
def get_chambre(chambre_id):
    # Charger la chambre avec sa maison, son propriétaire et ses médias
    chambre = Chambre.query.options(
        db.joinedload(Chambre.maison).joinedload(Maison.proprietaire),
        db.joinedload(Chambre.medias)
    ).get_or_404(chambre_id)
    return jsonify(serialize_chambre(chambre)), 200


@chambre_bp.route('/chambres/<int:chambre_id>', methods=['PUT'])
@role_required(['proprietaire'])
def update_chambre(chambre_id):
    current_user_identity = get_jwt_identity()
    owner_id = json.loads(current_user_identity)['id']

    chambre = db.session.query(Chambre).join(Maison).\
        filter(Chambre.id == chambre_id, Maison.proprietaire_id == owner_id).first()

    if not chambre:
        return jsonify({"message": "Chambre non trouvée ou ne vous appartient pas."}), 404

    data = request.get_json()

    if 'titre' in data:
        chambre.titre = data['titre']
    if 'description' in data:
        chambre.description = data['description']
    if 'taille' in data:
        chambre.taille = data['taille']
    if 'type' in data:
        chambre.type = data['type']
    if 'meublee' in data:
        chambre.meublee = bool(data['meublee'])
    if 'salle_de_bain' in data:
        chambre.salle_de_bain = bool(data['salle_de_bain'])

    # Utilise uniquement 'prix'
    if 'prix' in data:
        try: chambre.prix = float(data['prix'])
        except ValueError: return jsonify({"message": "Le prix doit être un nombre valide."}), 400

    if 'disponible' in data:
        chambre.disponible = bool(data['disponible'])

    db.session.commit()

    return jsonify({"message": "Chambre mise à jour avec succès.", "chambre": {
        "id": chambre.id,
        "maison_id": chambre.maison_id,
        "titre": chambre.titre,
        "description": chambre.description,
        "taille": chambre.taille,
        "type": chambre.type,
        "meublee": chambre.meublee,
        "salle_de_bain": chambre.salle_de_bain,
        "prix": float(chambre.prix), # Assurez-vous que c'est un float pour le JSON
        "disponible": chambre.disponible
    }}), 200


@chambre_bp.route('/chambres/<int:chambre_id>', methods=['DELETE'])
@role_required(roles=['proprietaire'])
def delete_chambre(chambre_id):
    chambre = Chambre.query.get_or_404(chambre_id)
    db.session.delete(chambre)
    db.session.commit()
    return jsonify({"message":"Chambre supprimée avec succès"}), 204
