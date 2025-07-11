
from flask import Blueprint, request, jsonify, current_app, url_for
from flask_jwt_extended import get_jwt_identity, jwt_required
from werkzeug.utils import secure_filename

from app.models import db, Utilisateur, Maison, Chambre, Contrat, Paiement, Media
from app.decorators import role_required
from datetime import date, datetime
import json
import os

proprietaire_bp = Blueprint('proprietaire_bp', __name__, url_prefix='/api')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']



# 1. En tant que propriétaire, je veux avoir la liste de mes clients (locataires)
@proprietaire_bp.route('/proprietaire/clients', methods=['GET'])
@role_required(['proprietaire'])
def get_proprietaire_clients():
    current_user_identity = get_jwt_identity()
    owner_id = json.loads(current_user_identity)['id']

    # Trouver tous les contrats liés aux chambres de ce propriétaire
    # et récupérer les locataires uniques de ces contrats
    locataires = db.session.query(Utilisateur).join(Contrat).join(Chambre).join(Maison). \
        filter(Maison.proprietaire_id == owner_id, Utilisateur.role == 'locataire'). \
        distinct().all()

    clients_data = [{
        "id": client.id,
        "nom_utilisateur": client.nom_utilisateur,
        "email": client.email,
        "telephone": client.telephone,
        "cni": client.cni
    } for client in locataires]

    return jsonify(clients_data), 200


@proprietaire_bp.route('/proprietaire/chambres', methods=['GET'])
@role_required(['proprietaire'])
def get_proprietaire_chambres():
    current_user_identity = get_jwt_identity()
    owner_id = json.loads(current_user_identity)['id']

    # Joindre les tables Maison et Media pour récupérer toutes les données nécessaires en une seule requête
    chambres = db.session.query(Chambre).join(Maison).\
        filter(Maison.proprietaire_id == owner_id).all()

    chambres_data = []
    for chambre in chambres:
        # Récupérer les contrats actifs pour la chambre
        active_contrats = [
            {
                "contrat_id": cont.id,
                "locataire_nom_utilisateur": cont.locataire.nom_utilisateur,
                "date_debut": cont.date_debut.isoformat(),
                "date_fin": cont.date_fin.isoformat(),
                "statut": cont.statut
            }
            for cont in chambre.contrats_chambre
            if cont.statut == 'actif' and cont.date_fin >= date.today()
        ]

        # Récupérer les médias (photos) associés à la chambre
        medias_data = [
            {
                "id": media.id,
                "url": media.url,
                "type": media.type,
                "description": media.description
            }
            for media in chambre.medias # Accès à la relation 'medias' définie dans le modèle Chambre
        ]

        chambres_data.append({
            "id": chambre.id,
            "maison_id": chambre.maison_id,
            "adresse_maison": chambre.maison.adresse,
            "ville_maison": chambre.maison.ville,  # NOUVEAU: Ajout de la ville de la maison
            "titre": chambre.titre,
            "description": chambre.description,
            "taille": chambre.taille,
            "type": chambre.type,
            "meublee": chambre.meublee,
            "salle_de_bain": chambre.salle_de_bain,
            "prix": float(chambre.prix),
            "disponible": chambre.disponible,
            "contrats_actifs": active_contrats,
            "medias": medias_data # NOUVEAU: Ajout des médias de la chambre
        })

    return jsonify(chambres_data), 200

# Route pour ajouter une nouvelle chambre (liée à une maison existante du propriétaire)
@proprietaire_bp.route('/proprietaire/chambres', methods=['POST'])
@role_required(['proprietaire'])
def add_chambre():
    current_user_identity = get_jwt_identity()
    owner_id = json.loads(current_user_identity)['id']
    data = request.get_json()

    required_fields = ['maison_id', 'titre', 'prix']
    for field in required_fields:
        if field not in data:
            return jsonify({"message": f"Le champ '{field}' est requis."}), 400

    # Vérifier que la maison_id existe et appartient bien au propriétaire
    maison = Maison.query.filter_by(id=data['maison_id'], proprietaire_id=owner_id).first()
    if not maison:
        return jsonify({"message": "Maison non trouvée ou ne vous appartient pas."}), 404

    try:
        prix = float(data['prix'])
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
        prix=prix,
        disponible=data.get('disponible', True)
    )

    db.session.add(new_chambre)
    maison.nombre_chambres += 1  # Incrémenter le nombre de chambres dans la maison
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
            "prix": float(new_chambre.prix),
            "disponible": new_chambre.disponible
        }
    }), 201


# Route pour modifier une chambre existante
@proprietaire_bp.route('/proprietaire/chambres/<int:chambre_id>', methods=['PUT'])
@role_required(['proprietaire'])
def update_chambre(chambre_id):
    current_user_identity = get_jwt_identity()
    owner_id = json.loads(current_user_identity)['id']

    chambre = db.session.query(Chambre).join(Maison). \
        filter(Chambre.id == chambre_id, Maison.proprietaire_id == owner_id).first()

    if not chambre:
        return jsonify({"message": "Chambre non trouvée ou ne vous appartient pas."}), 404

    data = request.get_json()

    # Mettre à jour les champs
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
    if 'prix' in data:
        try:
            chambre.prix = float(data['prix'])
        except ValueError:
            return jsonify({"message": "Le prix doit être un nombre valide."}), 400
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
        "prix": float(chambre.prix),
        "disponible": chambre.disponible
    }}), 200


# 3. et 4. En tant que propriétaire, je veux avoir la liste des payées/impayées et un dashboard
@proprietaire_bp.route('/proprietaire/paiements', methods=['GET'])
@role_required(['proprietaire'])
def get_proprietaire_paiements_dashboard():
    current_user_identity = get_jwt_identity()
    owner_id = json.loads(current_user_identity)['id']

    # Récupérer tous les paiements liés aux contrats des chambres des maisons de ce propriétaire
    # Joindre toutes les tables nécessaires pour filtrer par propriétaire
    paiements = db.session.query(Paiement).join(Contrat).join(Chambre).join(Maison). \
        filter(Maison.proprietaire_id == owner_id). \
        order_by(Paiement.date_echeance.desc()).all()  # Trie par date d'échéance

    paiements_data = []
    total_paye = 0.0
    total_impaye = 0.0  # Utilisez float pour les totaux monétaires

    for paiement in paiements:
        paiements_data.append({
            "id": paiement.id,
            "montant": float(paiement.montant),  # Convertir Numeric en float
            "date_echeance": paiement.date_echeance.isoformat(),
            "date_paiement": paiement.date_paiement.isoformat() if paiement.date_paiement else None,
            "statut": paiement.statut,
            "contrat_id": paiement.contrat_id,
            "chambre_titre": paiement.contrat.chambre.titre,
            "locataire_nom_utilisateur": paiement.contrat.locataire.nom_utilisateur
        })
        if paiement.statut == 'payé':
            total_paye += float(paiement.montant)
        elif paiement.statut == 'impayé':
            total_impaye += float(paiement.montant)

    dashboard_summary = {
        "total_paye": total_paye,
        "total_impaye": total_impaye,
        "nombre_paiements_payes": len([p for p in paiements if p.statut == 'payé']),
        "nombre_paiements_impayes": len([p for p in paiements if p.statut == 'impayé']),
        "nombre_paiements_partiels": len([p for p in paiements if p.statut == 'partiel'])
        # Ajouté pour un dashboard plus complet
    }

    return jsonify({
        "paiements": paiements_data,
        "dashboard_summary": dashboard_summary
    }), 200


# Route pour ajouter une maison (car un propriétaire doit d'abord avoir une maison pour y ajouter des chambres)
@proprietaire_bp.route('/proprietaire/maisons', methods=['POST'])
@role_required(['proprietaire'])
def add_maison():
    current_user_identity = get_jwt_identity()
    owner_id = json.loads(current_user_identity)['id']
    data = request.get_json()

    required_fields = ['adresse', 'ville']
    for field in required_fields:
        if field not in data:
            return jsonify({"message": f"Le champ '{field}' est requis."}), 400

    new_maison = Maison(
        adresse=data['adresse'],
        ville=data['ville'],
        description=data.get('description'),
        nombre_chambres=0,  # Initialisé à 0, sera incrémenté quand des chambres seront ajoutées
        proprietaire_id=owner_id
    )

    db.session.add(new_maison)
    db.session.commit()

    return jsonify({
        "message": "Maison ajoutée avec succès.",
        "maison": {
            "id": new_maison.id,
            "adresse": new_maison.adresse,
            "ville": new_maison.ville,
            "description": new_maison.description,
            "nombre_chambres": new_maison.nombre_chambres
        }
    }), 201


# Route pour lister les maisons du propriétaire
@proprietaire_bp.route('/proprietaire/maisons', methods=['GET'])
@role_required(['proprietaire'])
def get_proprietaire_maisons():
    current_user_identity = get_jwt_identity()
    owner_id = json.loads(current_user_identity)['id']

    maisons = Maison.query.filter_by(proprietaire_id=owner_id).all()

    maisons_data = [{
        "id": maison.id,
        "adresse": maison.adresse,
        "ville": maison.ville,
        "description": maison.description,
        "nombre_chambres": maison.nombre_chambres,
        "cree_le": maison.cree_le.isoformat()
    } for maison in maisons]

    return jsonify(maisons_data), 200


@proprietaire_bp.route('/chambres/<int:chambre_id>/medias', methods=['POST'])
@jwt_required()
# @proprietaire_required()
def upload_chambre_medias(chambre_id):
    current_user_identity = get_jwt_identity()
    owner_id = json.loads(current_user_identity)['id']

    chambre = Chambre.query.get(chambre_id)
    if not chambre:
        return jsonify({"message": "Chambre non trouvée"}), 404

    # Vérification de la propriété de la chambre (Sécurité essentielle)
    if chambre.maison.proprietaire_id != owner_id:
        return jsonify({"message": "Vous n'êtes pas autorisé à ajouter des médias à cette chambre."}), 403

    if 'files' not in request.files:
        return jsonify({"message": "Aucun fichier fourni sous la clé 'files'"}), 400

    uploaded_files = request.files.getlist('files')
    if not uploaded_files or all(f.filename == '' for f in uploaded_files):
        return jsonify({"message": "Aucun fichier sélectionné"}), 400

    uploaded_media_urls = []
    errors = []

    # Créer un sous-dossier pour chaque chambre dans UPLOAD_FOLDER
    # Chemin complet: static/uploads/chambres/<chambre_id>/
    chambre_upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'chambres', str(chambre.id))
    os.makedirs(chambre_upload_folder, exist_ok=True) # Crée le dossier s'il n'existe pas

    for file in uploaded_files:
        if file.filename == '':
            continue

        filename = secure_filename(file.filename)

        if not allowed_file(filename):
            errors.append(f"Type de fichier non autorisé pour {filename}.")
            continue

        try:
            # Construire le chemin complet où le fichier sera sauvegardé
            file_path = os.path.join(chambre_upload_folder, filename)
            file.save(file_path)

            # Générer l'URL accessible publiquement
            # Flask sert les fichiers du dossier 'static'.
            # L'URL sera donc /static/uploads/chambres/<chambre_id>/<filename>
            media_url = url_for('static', filename=f'uploads/chambres/{chambre.id}/{filename}', _external=True)

            new_media = Media(
                chambre_id=chambre.id,
                url=media_url,
                type='photo', # Vous pouvez déterminer le type plus finement via file.mimetype
                description=f"Photo de la chambre {chambre.titre} ({filename})"
            )
            db.session.add(new_media)
            db.session.commit()
            uploaded_media_urls.append({"id": new_media.id, "url": new_media.url})

        except Exception as e:
            db.session.rollback()
            errors.append(f"Échec du téléversement ou de l'enregistrement de {filename}: {str(e)}")
            print(f"Erreur d'upload backend (local): {e}")

    if errors:
        status_code = 400 if not uploaded_media_urls else 207
        return jsonify({
            "message": "Certains fichiers n'ont pas pu être traités.",
            "uploaded_count": len(uploaded_media_urls),
            "urls": uploaded_media_urls,
            "errors": errors
        }), status_code
    else:
        return jsonify({
            "message": f"{len(uploaded_media_urls)} médias téléversés avec succès.",
            "urls": uploaded_media_urls
        }), 201

# --- Route pour supprimer un média (ajustez le chemin du fichier local) ---
@proprietaire_bp.route('proprietaire/medias/<int:media_id>', methods=['DELETE'])
@jwt_required()
@role_required(['proprietaire'])
def delete_media(media_id):
    current_user_identity = get_jwt_identity()
    owner_id = json.loads(current_user_identity)['id']

    media = Media.query.get(media_id)
    if not media:
        return jsonify({"message": "Média non trouvé"}), 404

    # Vérifiez que l'utilisateur est bien le propriétaire de la chambre associée au média
    if media.chambre.maison.proprietaire_id != owner_id:
        return jsonify({"message": "Vous n'êtes pas autorisé à supprimer ce média."}), 403

    try:
        # Extraire le chemin relatif du fichier à partir de l'URL du média
        # Supposons que l'URL est /static/uploads/chambres/<chambre_id>/<filename>
        # current_app.config['UPLOAD_FOLDER'] est le chemin de base pour 'uploads'
        # On doit reconstruire le chemin absolu du fichier
        # Exemple: media.url = "http://localhost:5000/static/uploads/chambres/1/photo.jpg"
        # On veut: "uploads/chambres/1/photo.jpg"
        relative_path_start = media.url.find('/static/uploads/')
        if relative_path_start != -1:
            relative_path_from_static = media.url[relative_path_start + len('/static/'):]
            file_to_delete_path = os.path.join(current_app.root_path, 'static', relative_path_from_static)

            if os.path.exists(file_to_delete_path):
                os.remove(file_to_delete_path)
                print(f"Fichier local supprimé: {file_to_delete_path}")
            else:
                print(f"Avertissement: Fichier à supprimer non trouvé localement: {file_to_delete_path}")
        else:
            print(f"Avertissement: L'URL du média ne correspond pas au format de fichier local attendu: {media.url}")

        db.session.delete(media)
        db.session.commit()
        return jsonify({"message": "Média supprimé avec succès"}), 204
    except Exception as e:
        db.session.rollback()
        print(f"Erreur lors de la suppression du média (local): {e}")
        return jsonify({"message": "Erreur interne du serveur lors de la suppression du média."}), 500


@proprietaire_bp.route('/maisons/<int:maison_id>/chambres', methods=['GET'])
@jwt_required()
def get_chambres_by_maison_id(maison_id):
    current_user_identity = get_jwt_identity()
    user_id = json.loads(current_user_identity)['id']
    # user_role = json.loads(current_user_identity)['role'] # Si vous avez un champ 'role' dans le token

    maison = Maison.query.get(maison_id)

    if not maison:
        return jsonify({"message": "Maison non trouvée."}), 404

    # --- Vérification d'autorisation (TRÈS IMPORTANT) ---
    # Si seul le propriétaire de la maison doit voir ses chambres:
    if maison.proprietaire_id != user_id:
         return jsonify({"message": "Accès non autorisé à cette maison."}), 403

    # Si tous les utilisateurs authentifiés peuvent voir les chambres d'une maison donnée (par exemple, pour la recherche locataire):
    # Vous pouvez supprimer la vérification ci-dessus ou ajouter une logique conditionnelle ici
    # based on 'user_role' ou si l'endpoint est public (non @jwt_required)

    chambres = Chambre.query.filter_by(maison_id=maison_id).all()

    chambres_data = []
    for chambre in chambres:
        # Récupérer les contrats actifs (si pertinent pour cette vue)
        active_contrats = [
            {
                "contrat_id": cont.id,
                "locataire_nom_utilisateur": cont.locataire.nom_utilisateur,
                "date_debut": cont.date_debut.isoformat(),
                "date_fin": cont.date_fin.isoformat(),
                "statut": cont.statut
            }
            for cont in chambre.contrats_chambre if cont.statut == 'actif' and cont.date_fin >= date.today()
        ]

        # Récupérer les médias associés à la chambre
        medias_data = [
            {
                "id": media.id,
                "url": media.url,
                "type": media.type,
                "description": media.description
            }
            for media in chambre.medias
        ]

        chambres_data.append({
            "id": chambre.id,
            "maison_id": chambre.maison_id,
            "titre": chambre.titre,
            "description": chambre.description,
            "taille": chambre.taille,
            "type": chambre.type,
            "meublee": chambre.meublee,
            "salle_de_bain": chambre.salle_de_bain,
            "prix": float(chambre.prix),
            "disponible": chambre.disponible,
            "cree_le": chambre.cree_le.isoformat(), # Ajout de la date de création
            "contrats_actifs": active_contrats,
            "medias": medias_data # Inclure les médias
        })

    return jsonify(chambres_data), 200

@proprietaire_bp.route('/proprietaire/contrats', methods=['GET'])
@jwt_required()
def get_proprietaire_contrats():
    current_user_identity = get_jwt_identity()
    proprietaire_id = json.loads(current_user_identity)['id']

    # Récupérer tous les contrats pour les chambres qui appartiennent à ce propriétaire
    contrats = Contrat.query \
        .join(Chambre) \
        .join(Maison) \
        .filter(Maison.proprietaire_id == proprietaire_id) \
        .order_by(Contrat.date_debut.desc()) \
        .all()

    results = []
    for contrat in contrats:
        locataire = contrat.locataire # L'objet locataire via la relation
        chambre = contrat.chambre
        maison = chambre.maison

        results.append({
            "id": contrat.id,
            "locataire_id": locataire.id,
            "locataire_nom_utilisateur": locataire.nom_utilisateur, # Nom d'utilisateur du locataire
            "locataire_email": locataire.email, # Email du locataire
            "chambre_id": chambre.id,
            "chambre_titre": chambre.titre,
            "chambre_adresse": f"{maison.adresse}, {maison.ville}",
            "prix_mensuel_chambre": float(chambre.prix),
            "date_debut": contrat.date_debut.isoformat(),
            "date_fin": contrat.date_fin.isoformat(),
            "montant_caution": float(contrat.montant_caution) if contrat.montant_caution else None,
            "mois_caution": contrat.mois_caution,
            "mode_paiement": contrat.mode_paiement,
            "periodicite": contrat.periodicite,
            "statut": contrat.statut,
            "description": contrat.description,
            "cree_le": contrat.cree_le.isoformat(),
            # "paiements": [{"id": p.id, "montant": float(p.montant), "date_echeance": p.date_echeance.isoformat(), "statut": p.statut} for p in contrat.paiements]
        })
    return jsonify(results), 200


@proprietaire_bp.route('/proprietaire/paiements/<int:paiement_id>/marquer_paye', methods=['PUT'])
@jwt_required()
def marquer_paiement_paye(paiement_id):
    current_user_identity = get_jwt_identity()
    proprietaire_id = json.loads(current_user_identity)['id']

    paiement = Paiement.query.get(paiement_id)
    if not paiement:
        return jsonify({"message": "Paiement non trouvé."}), 404

    # Vérifier que le paiement appartient à une chambre de ce propriétaire
    if paiement.contrat.chambre.maison.proprietaire_id != proprietaire_id:
        return jsonify({"message": "Non autorisé à modifier ce paiement."}), 403

    if paiement.statut == 'payé':
        return jsonify({"message": "Ce paiement est déjà marqué comme payé."}), 400

    paiement.statut = 'payé'
    paiement.date_paiement = datetime.utcnow() # Enregistrer la date du paiement
    db.session.commit()

    return jsonify({"message": "Paiement marqué comme payé avec succès!"}), 200

# Optionnel: Endpoint pour obtenir les paiements d'un contrat spécifique pour le propriétaire
@proprietaire_bp.route('/proprietaire/contrats/<int:contrat_id>/paiements', methods=['GET'])
@jwt_required()
def get_proprietaire_contrat_paiements(contrat_id):
    current_user_identity = get_jwt_identity()
    proprietaire_id = json.loads(current_user_identity)['id']

    contrat = Contrat.query.get(contrat_id)
    if not contrat:
        return jsonify({"message": "Contrat non trouvé."}), 404

    # Vérifier que le contrat appartient à une chambre de ce propriétaire
    if contrat.chambre.maison.proprietaire_id != proprietaire_id:
        return jsonify({"message": "Non autorisé à voir les paiements de ce contrat."}), 403

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