import json
import os

from flask import Blueprint, request, jsonify, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename

from app import db
from app.decorators import role_required
from app.models import Chambre, Media
from app.serialization import serialize_media

media_bp = Blueprint('media_bp', __name__, url_prefix='/api')


# --- CRUD pour les Médias (User Story 9) ---

@media_bp.route('/medias', methods=['POST'])
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


# --- Route pour le téléversement de médias vers une chambre existante ---
# Supposons que les fichiers sont envoyés sous la clé 'files' dans le FormData
@media_bp.route('/medias', methods=['POST'])
@jwt_required()
@role_required(roles=['proprietaire'])
def upload_chambre_medias(chambre_id):
    current_user_identity = get_jwt_identity()
    current_user_id = json.loads(current_user_identity)['id']

    chambre = Chambre.query.get(chambre_id)
    if not chambre:
        return jsonify({"message": "Chambre non trouvée"}), 404

    if chambre.maison.proprietaire_id != current_user_id:
        return jsonify({"message": "Vous n'êtes pas autorisé à ajouter des médias à cette chambre"}), 403

    if 'files' not in request.files:
        return jsonify({"message": "Aucun fichier fourni"}), 400

    uploaded_files = request.files.getlist('files')
    if not uploaded_files:
        return jsonify({"message": "Aucun fichier sélectionné"}), 400

    uploaded_media_urls = []

    for file in uploaded_files:
        if file.filename == '':
            continue  # Passer les champs de fichier vides

        # Valider le type de fichier (exemple simple)
        if not file.content_type.startswith('image/'):
            return jsonify({"message": f"Fichier {file.filename} n'est pas une image valide"}), 400

        try:
            # --- STOCKAGE DU FICHIER ---
            # Option 1: Stockage local (POUR DÉVELOPPEMENT SEULEMENT)
            UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads', 'chambres', str(chambre_id))
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Crée le dossier s'il n'existe pas
            filename = secure_filename(file.filename)  # Sécuriser le nom du fichier
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)  # Sauvegarde le fichier localement
            media_url = f"/uploads/chambres/{chambre_id}/{filename}"

            print(f"Simulating upload of {filename}, URL: {media_url}")  # Pour voir ce qu'il se passe

            new_media = Media(
                chambre_id=chambre.id,
                url=media_url,
                type='photo',  # ou déterminer dynamiquement si c'est une vidéo
                description=f"Photo de la chambre {chambre.titre}"  # Description automatique
            )
            db.session.add(new_media)
            db.session.commit()  # Commit après chaque ajout de média, ou après la boucle
            uploaded_media_urls.append(media_url)

        except Exception as e:
            db.session.rollback()
            print(f"Erreur lors du téléversement ou de l'enregistrement de {file.filename}: {e}")
            return jsonify({"message": f"Échec du téléversement de {file.filename}: {str(e)}"}), 500

    return jsonify({
        "message": f"{len(uploaded_media_urls)} médias téléversés avec succès.",
        "urls": uploaded_media_urls
    }), 201


@media_bp.route('/medias', methods=['GET'])
def get_medias():
    medias = Media.query.all()
    return jsonify([serialize_media(m) for m in medias]), 200


@media_bp.route('/medias/<int:media_id>', methods=['GET'])
def get_media(media_id):
    media = Media.query.get_or_404(media_id)
    return jsonify(serialize_media(media)), 200


@media_bp.route('/medias/<int:media_id>', methods=['PUT'])
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


@media_bp.route('/medias/<int:media_id>', methods=['DELETE'])
@jwt_required()
@role_required(roles=['proprietaire'])
def delete_media(media_id):
    current_user_identity = get_jwt_identity()
    current_user_id = json.loads(current_user_identity)['id']

    media = Media.query.get(media_id)
    if not media:
        return jsonify({"message": "Média non trouvé"}), 404
    if media.chambre.maison.proprietaire.id != current_user_id:  # Accéder à la relation propriétaire
        return jsonify({"message": "Vous n'êtes pas autorisé à supprimer ce média"}), 403

    try:
        db.session.delete(media)
        db.session.commit()
        return jsonify({"message": "Média supprimé avec succès"}), 204  # 204 No Content
    except Exception as e:
        db.session.rollback()
        print(f"Erreur lors de la suppression du média: {e}")
