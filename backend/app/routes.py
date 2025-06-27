from flask import Blueprint, jsonify

api_bp = Blueprint('api', __name__)

@api_bp.route('/')
def index():
    return jsonify(message="Bienvenue sur l'API Social Logement !"), 200

@api_bp.route('/test')
def test_route():
    return jsonify(data="Ceci est une route de test de l'API backend."), 200