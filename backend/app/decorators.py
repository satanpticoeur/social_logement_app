import json
from functools import wraps

from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity


def role_required(roles):
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()  # S'assure que l'utilisateur est authentifié
        def decorator(*args, **kwargs):
            try:
                # Récupérer l'identité de l'utilisateur à partir du token
                json_identity_string = get_jwt_identity()
                identity_data = json.loads(json_identity_string)
                user_role = identity_data.get("role")

                if user_role not in roles:
                    return jsonify({"message": "Accès refusé: rôle insuffisant"}), 403

            except Exception as e:
                # Gérer les erreurs de décodage ou si le rôle n'est pas trouvé
                return jsonify({"message": f"Erreur de validation de rôle: {str(e)}"}), 401

            return fn(*args, **kwargs)

        return decorator

    return wrapper
