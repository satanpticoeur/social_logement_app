
from flask import Blueprint, request, jsonify, abort
from app.models import Utilisateur, db
from app.serialisation import serialize_utilisateur

user_bp = Blueprint('user_bp', __name__, url_prefix='/api')


@user_bp.route('/utilisateurs', methods=['POST'])
def create_utilisateur():
    data = request.get_json()
    if not data or not all(k in data for k in ['email', 'role']):
        abort(400, description="Email et role sont requis.")

    if Utilisateur.query.filter_by(email=data['email']).first():
        abort(409, description="Un utilisateur avec cet email existe déjà.")

    new_utilisateur = Utilisateur(
        nom_utilisateur=data.get('nom_utilisateur'),
        email=data['email'],
        telephone=data.get('telephone'),
        cni=data.get('cni'),
        role=data['role']
    )
    db.session.add(new_utilisateur)
    db.session.commit()
    return jsonify(serialize_utilisateur(new_utilisateur)), 201


@user_bp.route('/utilisateurs', methods=['GET'])
def get_utilisateurs():
    # User Story 1 & 6: Filtrer par rôle (locataire) ou obtenir tous les utilisateurs
    role_filter = request.args.get('role')
    query = Utilisateur.query
    if role_filter:
        query = query.filter_by(role=role_filter)
    utilisateurs = query.all()
    return jsonify([serialize_utilisateur(u) for u in utilisateurs]), 200


@user_bp.route('/utilisateurs/<int:utilisateur_id>', methods=['GET'])
def get_utilisateur(utilisateur_id):
    utilisateur = Utilisateur.query.get_or_404(utilisateur_id)
    return jsonify(serialize_utilisateur(utilisateur)), 200


@user_bp.route('/utilisateurs/<int:utilisateur_id>', methods=['PUT'])
def update_utilisateur(utilisateur_id):
    utilisateur = Utilisateur.query.get_or_404(utilisateur_id)
    data = request.get_json()

    if not data:
        abort(400, description="Données de mise à jour requises.")

    utilisateur.nom_utilisateur = data.get('nom_utilisateur', utilisateur.nom_utilisateur)
    if 'email' in data:  # Permettre la mise à jour de l'email, mais vérifier l'unicité
        if Utilisateur.query.filter(Utilisateur.email == data['email'], Utilisateur.id != utilisateur_id).first():
            abort(409, description="Cet email est déjà utilisé par un autre utilisateur.")
        utilisateur.email = data['email']
    utilisateur.telephone = data.get('telephone', utilisateur.telephone)
    utilisateur.cni = data.get('cni', utilisateur.cni)
    utilisateur.role = data.get('role', utilisateur.role)

    try:
        db.session.commit()
        return jsonify(serialize_utilisateur(utilisateur)), 200
    except Exception as e:
        db.session.rollback()
        abort(500, description=f"Erreur lors de la mise à jour de l'utilisateur: {str(e)}")


@user_bp.route('/utilisateurs/<int:utilisateur_id>', methods=['DELETE'])
def delete_utilisateur(utilisateur_id):
    utilisateur = Utilisateur.query.get_or_404(utilisateur_id)
    db.session.delete(utilisateur)
    db.session.commit()
    return jsonify(message="Utilisateur supprimé avec succès"), 204