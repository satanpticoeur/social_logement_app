import json
import os
from datetime import date, datetime

from dateutil.relativedelta import relativedelta
from flask import request, jsonify, current_app, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restx import Namespace, Resource, fields
from sqlalchemy.orm import joinedload
from werkzeug.utils import secure_filename

from app.decorators import role_required
from app.models import db, Utilisateur, Maison, Chambre, Contrat, Paiement, Media

proprietaire_ns = Namespace('proprietaire', description='Opérations spécifiques aux propriétaires')

# --- Fonctions utilitaires ---
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


# --- Modèles Flask-RESTx ---
# Modèle pour les messages de réponse génériques
message_model = proprietaire_ns.model('Message', {
    'message': fields.String(required=True, description='Message de statut de la réponse')
})

# Modèles pour Maison
maison_base_model = proprietaire_ns.model('MaisonBase', {
    'adresse': fields.String(required=True, description='Adresse de la maison'),
    'ville': fields.String(required=True, description='Ville où se trouve la maison'),
    'description': fields.String(description='Description de la maison', default=''),
    'nombre_chambres': fields.Integer(description='Nombre total de chambres dans la maison', default=0)
})

maison_response_model = proprietaire_ns.model('MaisonResponse', {
    'id': fields.Integer(readOnly=True, description='Identifiant unique de la maison'),
    'adresse': fields.String(required=True, description='Adresse de la maison'),
    'ville': fields.String(required=True, description='Ville où se trouve la maison'),
    'description': fields.String(description='Description de la maison'),
    'nombre_chambres': fields.Integer(description='Nombre de chambres dans la maison'),
    'cree_le': fields.String(description='Date de création de la maison (ISO format)')
})

# Modèles pour Chambre
chambre_media_model = proprietaire_ns.model('ChambreMedia', {
    'id': fields.Integer(readOnly=True, description='Identifiant du média'),
    'url': fields.String(required=True, description='URL du média'),
    'type': fields.String(description='Type de média (ex: photo, video)'),
    'description': fields.String(description='Description du média')
})

chambre_contrat_actif_model = proprietaire_ns.model('ChambreContratActif', {
    'contrat_id': fields.Integer(description='Identifiant du contrat actif'),
    'locataire_nom_utilisateur': fields.String(description='Nom d\'utilisateur du locataire'),
    'date_debut': fields.String(description='Date de début du contrat (ISO format)'),
    'date_fin': fields.String(description='Date de fin du contrat (ISO format)'),
    'statut': fields.String(description='Statut du contrat')
})

chambre_base_model = proprietaire_ns.model('ChambreBase', {
    'maison_id': fields.Integer(required=True, description='Identifiant de la maison parente'),
    'titre': fields.String(required=True, description='Titre de la chambre'),
    'description': fields.String(description='Description de la chambre', default=''),
    'taille': fields.String(description='Taille de la chambre (ex: "15m²")', default=''),
    'type': fields.String(description='Type de chambre (ex: "studio", "T1")', default=''),
    'meublee': fields.Boolean(description='La chambre est-elle meublée ?', default=False),
    'salle_de_bain': fields.Boolean(description='La chambre a-t-elle une salle de bain privée ?', default=False),
    'prix': fields.Float(required=True, description='Prix mensuel de la chambre'),
    'disponible': fields.Boolean(description='La chambre est-elle disponible ?', default=True)
})

chambre_response_model = proprietaire_ns.model('ChambreResponse', {
    'id': fields.Integer(readOnly=True, description='Identifiant unique de la chambre'),
    'maison_id': fields.Integer(required=True, description='Identifiant de la maison parente'),
    'titre': fields.String(required=True, description='Titre de la chambre'),
    'description': fields.String(description='Description de la chambre'),
    'taille': fields.String(description='Taille de la chambre'),
    'type': fields.String(description='Type de chambre'),
    'meublee': fields.Boolean(description='La chambre est-elle meublée ?'),
    'salle_de_bain': fields.Boolean(description='La chambre a-t-elle une salle de bain privée ?'),
    'prix': fields.Float(description='Prix mensuel de la chambre'),
    'disponible': fields.Boolean(description='La chambre est-elle disponible ?')
})

chambre_detailed_response_model = proprietaire_ns.model('ChambreDetailedResponse', {
    'id': fields.Integer(readOnly=True, description='Identifiant unique de la chambre'),
    'maison_id': fields.Integer(description='Identifiant de la maison parente'),
    'adresse_maison': fields.String(description='Adresse de la maison parente'),
    'ville_maison': fields.String(description='Ville de la maison parente'),
    'titre': fields.String(description='Titre de la chambre'),
    'description': fields.String(description='Description de la chambre'),
    'taille': fields.String(description='Taille de la chambre'),
    'type': fields.String(description='Type de chambre'),
    'meublee': fields.Boolean(description='La chambre est-elle meublée ?'),
    'salle_de_bain': fields.Boolean(description='La chambre a-t-elle une salle de bain privée ?'),
    'prix': fields.Float(description='Prix mensuel de la chambre'),
    'disponible': fields.Boolean(description='La chambre est-elle disponible ?'),
    'cree_le': fields.String(description='Date de création de la chambre (ISO format)'),
    'contrats_actifs': fields.List(fields.Nested(chambre_contrat_actif_model), description='Liste des contrats actifs pour cette chambre'),
    'medias': fields.List(fields.Nested(chambre_media_model), description='Liste des médias (photos) associés à la chambre')
})

# Modèles pour Client (Locataire)
client_response_model = proprietaire_ns.model('ClientResponse', {
    'id': fields.Integer(readOnly=True, description='Identifiant unique du locataire'),
    'nom_utilisateur': fields.String(description='Nom d\'utilisateur du locataire'),
    'email': fields.String(description='Email du locataire'),
    'telephone': fields.String(description='Numéro de téléphone du locataire'),
    'cni': fields.String(description='Numéro de CNI du locataire')
})


# Modèles pour Contrat
contrat_base_model = proprietaire_ns.model('ContratBase', {
    'locataire_id': fields.Integer(required=True, description='ID du locataire'),
    'chambre_id': fields.Integer(required=True, description='ID de la chambre'),
    'date_debut': fields.Date(required=True, description='Date de début du contrat (YYYY-MM-DD)'),
    'date_fin': fields.Date(required=True, description='Date de fin du contrat (YYYY-MM-DD)'),
    'montant_caution': fields.Float(description='Montant de la caution'),
    'mois_caution': fields.Integer(description='Nombre de mois couverts par la caution'),
    'mode_paiement': fields.String(description='Mode de paiement (ex: "virement", "espèces")'),
    'periodicite': fields.String(description='Périodicité du paiement (ex: "mensuel", "trimestriel")'),
    'statut': fields.String(description='Statut du contrat (ex: "actif", "en_attente_validation", "rejete", "resilie", "termine")'),
    'description': fields.String(description='Description du contrat')
})

contrat_response_model = proprietaire_ns.model('ContratResponse', {
    'id': fields.Integer(readOnly=True, description='Identifiant unique du contrat'),
    'locataire_id': fields.Integer(description='Identifiant du locataire'),
    'locataire_nom_utilisateur': fields.String(description='Nom d\'utilisateur du locataire'),
    'locataire_email': fields.String(description='Email du locataire'),
    'chambre_id': fields.Integer(description='Identifiant de la chambre'),
    'chambre_titre': fields.String(description='Titre de la chambre'),
    'chambre_adresse': fields.String(description='Adresse de la chambre'),
    'prix_mensuel_chambre': fields.Float(description='Prix mensuel de la chambre'),
    'date_debut': fields.String(description='Date de début du contrat (ISO format)'),
    'date_fin': fields.String(description='Date de fin du contrat (ISO format)'),
    'montant_caution': fields.Float(description='Montant de la caution'),
    'mois_caution': fields.Integer(description='Nombre de mois de caution'),
    'mode_paiement': fields.String(description='Mode de paiement'),
    'periodicite': fields.String(description='Périodicité de paiement'),
    'statut': fields.String(description='Statut du contrat'),
    'description': fields.String(description='Description du contrat'),
    'cree_le': fields.String(description='Date de création du contrat (ISO format)')
})

contrat_detailed_paiement_model = proprietaire_ns.model('ContratDetailedPaiement', {
    'id': fields.Integer(readOnly=True, description='Identifiant du paiement'),
    'montant': fields.Float(description='Montant du paiement'),
    'date_echeance': fields.String(description='Date d\'échéance du paiement (ISO format)'),
    'date_paiement': fields.String(description='Date du paiement (ISO format)'),
    'statut': fields.String(description='Statut du paiement (ex: "payé", "impayé")')
})

contrat_detailed_response_model = proprietaire_ns.model('ContratDetailedResponse', {
    'id': fields.Integer(readOnly=True, description='Identifiant unique du contrat'),
    'locataire_id': fields.Integer(description='Identifiant du locataire'),
    'locataire_nom_utilisateur': fields.String(description='Nom d\'utilisateur du locataire'),
    'locataire_email': fields.String(description='Email du locataire'),
    'chambre_id': fields.Integer(description='Identifiant de la chambre'),
    'chambre_titre': fields.String(description='Titre de la chambre'),
    'chambre_adresse': fields.String(description='Adresse de la chambre'),
    'prix_mensuel_chambre': fields.Float(description='Prix mensuel de la chambre'),
    'date_debut': fields.String(description='Date de début du contrat (ISO format)'),
    'date_fin': fields.String(description='Date de fin du contrat (ISO format)'),
    'montant_caution': fields.Float(description='Montant de la caution'),
    'mois_caution': fields.Integer(description='Nombre de mois de caution'),
    'mode_paiement': fields.String(description='Mode de paiement'),
    'periodicite': fields.String(description='Périodicité de paiement'),
    'statut': fields.String(description='Statut du contrat'),
    'description': fields.String(description='Description du contrat'),
    'cree_le': fields.String(description='Date de création du contrat (ISO format)'),
    'paiements': fields.List(fields.Nested(contrat_detailed_paiement_model), description='Liste des paiements associés à ce contrat')
})

# Modèles pour Paiement
paiement_response_model = proprietaire_ns.model('PaiementResponse', {
    'id': fields.Integer(readOnly=True, description='Identifiant unique du paiement'),
    'montant': fields.Float(description='Montant du paiement'),
    'date_echeance': fields.String(description='Date d\'échéance du paiement (ISO format)'),
    'date_paiement': fields.String(description='Date du paiement (ISO format)'),
    'statut': fields.String(description='Statut du paiement'),
    'contrat_id': fields.Integer(description='Identifiant du contrat associé'),
    'chambre_titre': fields.String(description='Titre de la chambre du contrat'),
    'locataire_nom_utilisateur': fields.String(description='Nom d\'utilisateur du locataire')
})

# Modèles pour Dashboard Summary
dashboard_summary_model = proprietaire_ns.model('DashboardSummary', {
    'total_paye': fields.Float(description='Montant total des paiements marqués comme payés'),
    'total_impaye': fields.Float(description='Montant total des paiements marqués comme impayés'),
    'nombre_paiements_payes': fields.Integer(description='Nombre de paiements marqués comme payés'),
    'nombre_paiements_impayes': fields.Integer(description='Nombre de paiements marqués comme impayés'),
    'nombre_paiements_partiels': fields.Integer(description='Nombre de paiements marqués comme partiels')
})

# Modèle pour la réponse combinée paiements et dashboard
paiements_dashboard_response_model = proprietaire_ns.model('PaiementsDashboardResponse', {
    'paiements': fields.List(fields.Nested(paiement_response_model), description='Liste des paiements'),
    'dashboard_summary': fields.Nested(dashboard_summary_model, description='Résumé du tableau de bord des paiements')
})

# Modèles pour le téléversement de médias
# Pour les fichiers, Flask-RESTx n'a pas de type direct dans fields.
# On utilise reqparse pour la documentation, et pour la réponse, on a déjà un modèle
media_upload_response_model = proprietaire_ns.model('MediaUploadResponse', {
    'id': fields.Integer(description='Identifiant du média téléversé'),
    'url': fields.String(description='URL du média téléversé')
})

media_upload_list_response_model = proprietaire_ns.model('MediaUploadListResponse', {
    'message': fields.String(description='Message de statut'),
    'uploaded_count': fields.Integer(description='Nombre de fichiers téléversés avec succès'),
    'urls': fields.List(fields.Nested(media_upload_response_model), description='Liste des URLs des médias téléversés'),
    'errors': fields.List(fields.String, description='Liste des erreurs rencontrées')
})

media_delete_response_model = proprietaire_ns.model('MediaDeleteResponse', {
    'message': fields.String(description='Message de suppression du média')
})

# Modèle pour les demandes de location en attente
demande_location_attente_model = proprietaire_ns.model('DemandeLocationAttente', {
    'id': fields.Integer(description='ID du contrat (demande)'),
    'locataire_id': fields.Integer(description='ID du locataire'),
    'locataire_nom': fields.String(description='Nom du locataire'),
    'chambre_id': fields.Integer(description='ID de la chambre'),
    'chambre_titre': fields.String(description='Titre de la chambre'),
    'date_debut': fields.String(description='Date de début souhaitée (ISO format)'),
    'date_fin': fields.String(description='Date de fin souhaitée (ISO format)'),
    'montant_caution': fields.Float(description='Montant de la caution'),
    'duree_mois': fields.Integer(description='Durée en mois'),
    'statut': fields.String(description='Statut de la demande')
})

# --- Routes Converties ---

# Route pour lister les maisons du propriétaire
@proprietaire_ns.route('/maisons')
class ProprietaireMaisons(Resource):
    @jwt_required()
    @proprietaire_ns.doc(security='csrfToken')
    @role_required(['proprietaire'])
    @proprietaire_ns.marshal_with(maison_response_model, as_list=True, code=200)
    @proprietaire_ns.response(401, 'Non autorisé', message_model)
    @proprietaire_ns.response(403, 'Accès refusé (rôle incorrect)', message_model)
    @proprietaire_ns.response(500, 'Erreur interne du serveur', message_model)
    def get(self):
        """
        Liste toutes les maisons appartenant au propriétaire connecté.
        """
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

        return maisons_data, 200

    @jwt_required()
    @proprietaire_ns.doc(security='csrfToken')
    @role_required(['proprietaire'])
    @proprietaire_ns.expect(maison_base_model, validate=True)
    @proprietaire_ns.marshal_with(maison_response_model, code=201)
    @proprietaire_ns.response(400, 'Champs requis manquants', message_model)
    @proprietaire_ns.response(401, 'Non autorisé', message_model)
    @proprietaire_ns.response(403, 'Accès refusé (rôle incorrect)', message_model)
    @proprietaire_ns.response(500, 'Erreur interne du serveur', message_model)
    def post(self):
        """
        Ajoute une nouvelle maison pour le propriétaire connecté.
        """
        current_user_identity = get_jwt_identity()
        owner_id = json.loads(current_user_identity)['id']
        data = proprietaire_ns.payload

        # Les validations des champs requis sont déjà gérées par proprietaire_ns.expect(..., validate=True)
        # si les champs sont marqués required=True dans le modèle.

        new_maison = Maison(
            adresse=data['adresse'],
            ville=data['ville'],
            description=data.get('description'),
            nombre_chambres=0,
            proprietaire_id=owner_id
        )

        try:
            db.session.add(new_maison)
            db.session.commit()
            return {
                "message": "Maison ajoutée avec succès.",
                "id": new_maison.id,
                "adresse": new_maison.adresse,
                "ville": new_maison.ville,
                "description": new_maison.description,
                "nombre_chambres": new_maison.nombre_chambres,
                "cree_le": new_maison.cree_le.isoformat() if new_maison.cree_le else None
            }, 201
        except Exception as e:
            db.session.rollback()
            proprietaire_ns.abort(500, f"Erreur lors de l'ajout de la maison: {str(e)}")


# Route pour lister toutes les chambres du propriétaire
@proprietaire_ns.route('/chambres')
class ProprietaireChambres(Resource):
    @proprietaire_ns.doc(security='apikey')
    @role_required(['proprietaire'])
    @proprietaire_ns.marshal_with(chambre_detailed_response_model, as_list=True, code=200)
    @proprietaire_ns.response(401, 'Non autorisé', message_model)
    @proprietaire_ns.response(403, 'Accès refusé (rôle incorrect)', message_model)
    @proprietaire_ns.response(500, 'Erreur interne du serveur', message_model)
    def get(self):
        """
        Liste toutes les chambres appartenant au propriétaire connecté, avec leurs contrats actifs et médias.
        """
        current_user_identity = get_jwt_identity()
        owner_id = json.loads(current_user_identity)['id']

        chambres = db.session.query(Chambre).join(Maison). \
            filter(Maison.proprietaire_id == owner_id).all()

        chambres_data = []
        for chambre in chambres:
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
                "adresse_maison": chambre.maison.adresse,
                "ville_maison": chambre.maison.ville,
                "titre": chambre.titre,
                "description": chambre.description,
                "taille": chambre.taille,
                "type": chambre.type,
                "meublee": chambre.meublee,
                "salle_de_bain": chambre.salle_de_bain,
                "prix": float(chambre.prix),
                "disponible": chambre.disponible,
                "contrats_actifs": active_contrats,
                "medias": medias_data
            })
        return chambres_data, 200

    @proprietaire_ns.doc(security='apikey')
    @role_required(['proprietaire'])
    @proprietaire_ns.expect(chambre_base_model, validate=True)
    @proprietaire_ns.marshal_with(chambre_response_model, code=201)
    @proprietaire_ns.response(400, 'Champs requis manquants ou invalides', message_model)
    @proprietaire_ns.response(404, 'Maison non trouvée ou ne vous appartient pas', message_model)
    @proprietaire_ns.response(401, 'Non autorisé', message_model)
    @proprietaire_ns.response(403, 'Accès refusé (rôle incorrect)', message_model)
    @proprietaire_ns.response(500, 'Erreur interne du serveur', message_model)
    def post(self):
        """
        Ajoute une nouvelle chambre à une maison existante du propriétaire.
        """
        current_user_identity = get_jwt_identity()
        owner_id = json.loads(current_user_identity)['id']
        data = proprietaire_ns.payload

        maison = Maison.query.filter_by(id=data['maison_id'], proprietaire_id=owner_id).first()
        if not maison:
            proprietaire_ns.abort(404, "Maison non trouvée ou ne vous appartient pas.")

        try:
            prix = float(data['prix'])
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
        except ValueError:
            proprietaire_ns.abort(400, "Le prix doit être un nombre valide.")



        try:
            db.session.add(new_chambre)
            maison.nombre_chambres += 1
            db.session.commit()
            return {
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
            }, 201
        except Exception as e:
            db.session.rollback()
            proprietaire_ns.abort(500, f"Erreur lors de l'ajout de la chambre: {str(e)}")


# Route pour obtenir les chambres d'une maison spécifique
@proprietaire_ns.route('/maisons/<int:maison_id>/chambres')
class ChambresByMaison(Resource):
    @proprietaire_ns.doc(security='apikey')
    @jwt_required()
    @proprietaire_ns.marshal_with(chambre_detailed_response_model, as_list=True, code=200)
    @proprietaire_ns.response(401, 'Non autorisé', message_model)
    @proprietaire_ns.response(403, 'Accès non autorisé à cette maison', message_model)
    @proprietaire_ns.response(404, 'Maison non trouvée', message_model)
    @proprietaire_ns.response(500, 'Erreur interne du serveur', message_model)
    def get(self, maison_id):
        """
        Récupère toutes les chambres d'une maison spécifique appartenant au propriétaire.
        """
        current_user_identity = get_jwt_identity()
        user_id = json.loads(current_user_identity)['id']

        maison = Maison.query.get(maison_id)

        if not maison:
            proprietaire_ns.abort(404, "Maison non trouvée.")

        if maison.proprietaire_id != user_id:
            proprietaire_ns.abort(403, "Accès non autorisé à cette maison.")

        chambres = Chambre.query.filter_by(maison_id=maison_id).all()

        chambres_data = []
        for chambre in chambres:
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
                "cree_le": chambre.cree_le.isoformat(),
                "contrats_actifs": active_contrats,
                "medias": medias_data
            })

        return chambres_data, 200


# Route pour lister les clients (locataires) du propriétaire
@proprietaire_ns.route('/clients')
class ProprietaireClients(Resource):
    @proprietaire_ns.doc(security='apikey')
    @role_required(['proprietaire'])
    @proprietaire_ns.marshal_with(client_response_model, as_list=True, code=200)
    @proprietaire_ns.response(401, 'Non autorisé', message_model)
    @proprietaire_ns.response(403, 'Accès refusé (rôle incorrect)', message_model)
    @proprietaire_ns.response(500, 'Erreur interne du serveur', message_model)
    def get(self):
        """
        Liste tous les locataires ayant un contrat actif ou passé avec une chambre du propriétaire connecté.
        """
        current_user_identity = get_jwt_identity()
        owner_id = json.loads(current_user_identity)['id']

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

        return clients_data, 200


# Route pour gérer les opérations sur une chambre spécifique (Mise à jour)
@proprietaire_ns.route('/chambres/<int:chambre_id>')
class ChambreOperations(Resource):
    @proprietaire_ns.doc(security='apikey')
    @role_required(['proprietaire'])
    @proprietaire_ns.expect(chambre_base_model, validate=True)
    @proprietaire_ns.marshal_with(chambre_response_model, code=200)
    @proprietaire_ns.response(400, 'Données de mise à jour invalides', message_model)
    @proprietaire_ns.response(404, 'Chambre non trouvée ou ne vous appartient pas', message_model)
    @proprietaire_ns.response(401, 'Non autorisé', message_model)
    @proprietaire_ns.response(403, 'Accès refusé (rôle incorrect)', message_model)
    @proprietaire_ns.response(500, 'Erreur interne du serveur', message_model)
    def put(self, chambre_id):
        """
        Met à jour les informations d'une chambre spécifique.
        """
        current_user_identity = get_jwt_identity()
        owner_id = json.loads(current_user_identity)['id']

        chambre = db.session.query(Chambre).join(Maison). \
            filter(Chambre.id == chambre_id, Maison.proprietaire_id == owner_id).first()

        if not chambre:
            proprietaire_ns.abort(404, "Chambre non trouvée ou ne vous appartient pas.")

        data = proprietaire_ns.payload

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
                proprietaire_ns.abort(400, "Le prix doit être un nombre valide.")
        if 'disponible' in data:
            chambre.disponible = bool(data['disponible'])

        try:
            db.session.commit()
            return {
                "message": "Chambre mise à jour avec succès.",
                "chambre": {
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
                }
            }, 200
        except Exception as e:
            db.session.rollback()
            proprietaire_ns.abort(500, f"Erreur lors de la mise à jour de la chambre: {str(e)}")


# Route pour lister tous les contrats du propriétaire
@proprietaire_ns.route('/contrats')
class ProprietaireContrats(Resource):
    @proprietaire_ns.doc(security='apikey')
    @jwt_required()
    @proprietaire_ns.marshal_with(contrat_response_model, as_list=True, code=200)
    @proprietaire_ns.response(401, 'Non autorisé', message_model)
    @proprietaire_ns.response(403, 'Accès refusé. Seuls les propriétaires peuvent voir leurs contrats.', message_model)
    @proprietaire_ns.response(500, 'Erreur interne du serveur', message_model)
    def get(self):
        """
        Liste tous les contrats (actifs, rejetés, résiliés, terminés) liés aux chambres du propriétaire connecté.
        """
        current_user_identity = get_jwt_identity()
        current_user_id = json.loads(current_user_identity)['id']
        proprietaire = Utilisateur.query.get(current_user_id)

        if not proprietaire or proprietaire.role != 'proprietaire':
            proprietaire_ns.abort(403, "Accès refusé. Seuls les propriétaires peuvent voir leurs contrats.")

        contrats = Contrat.query.options(
            joinedload(Contrat.locataire),
            joinedload(Contrat.chambre).joinedload(Chambre.maison)
        ).filter(
            Contrat.chambre.has(Chambre.maison.has(Maison.proprietaire_id == proprietaire.id)),
            Contrat.statut.in_(['actif', 'rejete', 'resilie', 'termine'])
        ).order_by(Contrat.date_debut.desc()).all()

        results = []
        for contrat in contrats:
            locataire_nom = contrat.locataire.nom_utilisateur if contrat.locataire else 'N/A'
            locataire_email = contrat.locataire.email if contrat.locataire else 'N/A'
            chambre_titre = contrat.chambre.titre if contrat.chambre else 'N/A'
            chambre_adresse = contrat.chambre.maison.adresse if contrat.chambre and contrat.chambre.maison else 'N/A'
            prix_mensuel_chambre = float(contrat.chambre.prix) if contrat.chambre else 0.0

            results.append({
                "id": contrat.id,
                "locataire_id": contrat.locataire.id,
                "locataire_nom_utilisateur": locataire_nom,
                "locataire_email": locataire_email,
                "chambre_id": contrat.chambre.id,
                "chambre_titre": chambre_titre,
                "chambre_adresse": chambre_adresse,
                "prix_mensuel_chambre": prix_mensuel_chambre,
                "date_debut": contrat.date_debut.isoformat(),
                "date_fin": contrat.date_fin.isoformat(),
                "montant_caution": float(contrat.montant_caution),
                "mois_caution": contrat.mois_caution,
                "mode_paiement": contrat.mode_paiement,
                "periodicite": contrat.periodicite,
                "statut": contrat.statut,
                "description": contrat.description,
                "cree_le": contrat.cree_le.isoformat()
            })
        return results, 200

# Route pour obtenir les détails d'un contrat spécifique
@proprietaire_ns.route('/contrats/<int:contrat_id>/details')
class ContratDetails(Resource):
    @proprietaire_ns.doc(security='apikey')
    @jwt_required()
    @proprietaire_ns.marshal_with(contrat_detailed_response_model, code=200)
    @proprietaire_ns.response(401, 'Non autorisé', message_model)
    @proprietaire_ns.response(403, 'Accès refusé', message_model)
    @proprietaire_ns.response(404, 'Contrat non trouvé ou vous n\'êtes pas le propriétaire', message_model)
    @proprietaire_ns.response(500, 'Erreur interne du serveur', message_model)
    def get(self, contrat_id):
        """
        Récupère les détails d'un contrat spécifique, incluant tous les paiements associés.
        """
        current_user_identity = get_jwt_identity()
        current_user_id = json.loads(current_user_identity)['id']

        proprietaire = Utilisateur.query.get(current_user_id)

        if not proprietaire or proprietaire.role != 'proprietaire':
            proprietaire_ns.abort(403, "Accès refusé.")

        contrat = Contrat.query.options(
            joinedload(Contrat.locataire),
            joinedload(Contrat.chambre).joinedload(Chambre.maison),
            joinedload(Contrat.paiements)
        ).filter(
            Contrat.id == contrat_id,
            Contrat.chambre.has(Chambre.maison.has(Maison.proprietaire_id == proprietaire.id))
        ).first()

        if not contrat:
            proprietaire_ns.abort(404, "Contrat non trouvé ou vous n'êtes pas le propriétaire.")

        locataire_nom = contrat.locataire.nom_utilisateur if contrat.locataire else 'N/A'
        locataire_email = contrat.locataire.email if contrat.locataire else 'N/A'
        chambre_titre = contrat.chambre.titre if contrat.chambre else 'N/A'
        chambre_adresse = contrat.chambre.maison.adresse if contrat.chambre and contrat.chambre.maison else 'N/A'
        prix_mensuel_chambre = float(contrat.chambre.prix) if contrat.chambre else 0.0

        paiements_data = []
        for paiement in contrat.paiements:
            paiements_data.append({
                "id": paiement.id,
                "montant": float(paiement.montant),
                "date_echeance": paiement.date_echeance.isoformat(),
                "date_paiement": paiement.date_paiement.isoformat() if paiement.date_paiement else None,
                "statut": paiement.statut,
            })

        contrat_data = {
            "id": contrat.id,
            "locataire_id": contrat.locataire.id,
            "locataire_nom_utilisateur": locataire_nom,
            "locataire_email": locataire_email,
            "chambre_id": contrat.chambre.id,
            "chambre_titre": chambre_titre,
            "chambre_adresse": chambre_adresse,
            "prix_mensuel_chambre": prix_mensuel_chambre,
            "date_debut": contrat.date_debut.isoformat(),
            "date_fin": contrat.date_fin.isoformat(),
            "montant_caution": float(contrat.montant_caution),
            "mois_caution": contrat.mois_caution,
            "mode_paiement": contrat.mode_paiement,
            "periodicite": contrat.periodicite,
            "statut": contrat.statut,
            "description": contrat.description,
            "cree_le": contrat.cree_le.isoformat(),
            "paiements": paiements_data
        }
        return contrat_data, 200


# Route pour résilier un contrat
@proprietaire_ns.route('/contrats/<int:contrat_id>/resilier')
class ContratResiliation(Resource):
    @proprietaire_ns.doc(security='apikey')
    @jwt_required()
    @proprietaire_ns.marshal_with(message_model, code=200)
    @proprietaire_ns.response(400, 'Impossible de résilier un contrat avec ce statut', message_model)
    @proprietaire_ns.response(401, 'Non autorisé', message_model)
    @proprietaire_ns.response(403, 'Accès refusé', message_model)
    @proprietaire_ns.response(404, 'Contrat non trouvé ou vous n\'êtes pas le propriétaire', message_model)
    @proprietaire_ns.response(500, 'Erreur interne du serveur', message_model)
    def put(self, contrat_id):
        """
        Résilie un contrat de location actif.
        """
        current_user_identity = get_jwt_identity()
        current_user_id = json.loads(current_user_identity)['id']
        proprietaire = Utilisateur.query.get(current_user_id)

        if not proprietaire or proprietaire.role != 'proprietaire':
            proprietaire_ns.abort(403, "Accès refusé.")

        contrat = Contrat.query.options(
            joinedload(Contrat.chambre).joinedload(Chambre.maison)
        ).filter(
            Contrat.id == contrat_id,
            Contrat.chambre.has(Chambre.maison.has(Maison.proprietaire_id == proprietaire.id))
        ).first()

        if not contrat:
            proprietaire_ns.abort(404, "Contrat non trouvé ou vous n'êtes pas le propriétaire.")

        if contrat.statut not in ['actif']:
            proprietaire_ns.abort(400, f"Impossible de résilier un contrat avec le statut '{contrat.statut}'.")

        try:
            contrat.statut = 'resilie'
            db.session.add(contrat)

            chambre = Chambre.query.get(contrat.chambre_id)
            if chambre:
                autres_contrats_actifs = Contrat.query.filter(
                    Contrat.chambre_id == chambre.id,
                    Contrat.id != contrat.id,
                    Contrat.statut == 'actif'
                ).first()

                if not autres_contrats_actifs:
                    chambre.disponible = True
                    db.session.add(chambre)

            db.session.commit()
            return {"message": "Contrat résilié avec succès."}, 200
        except Exception as e:
            db.session.rollback()
            proprietaire_ns.abort(500, f"Erreur lors de la résiliation du contrat: {str(e)}")


# Route pour obtenir les paiements et un résumé du tableau de bord
@proprietaire_ns.route('/paiements')
class ProprietairePaiementsDashboard(Resource):
    @proprietaire_ns.doc(security='apikey')
    @role_required(['proprietaire'])
    @proprietaire_ns.marshal_with(paiements_dashboard_response_model, code=200)
    @proprietaire_ns.response(401, 'Non autorisé', message_model)
    @proprietaire_ns.response(403, 'Accès refusé (rôle incorrect)', message_model)
    @proprietaire_ns.response(500, 'Erreur interne du serveur', message_model)
    def get(self):
        """
        Récupère tous les paiements liés aux chambres du propriétaire et un résumé du tableau de bord.
        """
        current_user_identity = get_jwt_identity()
        owner_id = json.loads(current_user_identity)['id']

        paiements = db.session.query(Paiement).join(Contrat).join(Chambre).join(Maison). \
            filter(Maison.proprietaire_id == owner_id). \
            order_by(Paiement.date_echeance.desc()).all()

        paiements_data = []
        total_paye = 0.0
        total_impaye = 0.0

        for paiement in paiements:
            paiements_data.append({
                "id": paiement.id,
                "montant": float(paiement.montant),
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
        }

        return {
            "paiements": paiements_data,
            "dashboard_summary": dashboard_summary
        }, 200


# Route pour obtenir les paiements d'un contrat spécifique
@proprietaire_ns.route('/contrats/<int:contrat_id>/paiements')
class ContratPaiements(Resource):
    @proprietaire_ns.doc(security='apikey')
    @jwt_required()
    @proprietaire_ns.marshal_with(contrat_detailed_paiement_model, as_list=True, code=200)
    @proprietaire_ns.response(401, 'Non autorisé', message_model)
    @proprietaire_ns.response(403, 'Non autorisé à voir les paiements de ce contrat', message_model)
    @proprietaire_ns.response(404, 'Contrat non trouvé', message_model)
    @proprietaire_ns.response(500, 'Erreur interne du serveur', message_model)
    def get(self, contrat_id):
        """
        Récupère tous les paiements associés à un contrat spécifique du propriétaire.
        """
        current_user_identity = get_jwt_identity()
        proprietaire_id = json.loads(current_user_identity)['id']

        contrat = Contrat.query.get(contrat_id)
        if not contrat:
            proprietaire_ns.abort(404, "Contrat non trouvé.")

        if not (contrat.chambre and contrat.chambre.maison and contrat.chambre.maison.proprietaire_id == proprietaire_id):
            proprietaire_ns.abort(403, "Non autorisé à voir les paiements de ce contrat.")

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
        return results, 200

# Route pour marquer un paiement comme payé
@proprietaire_ns.route('/paiements/<int:paiement_id>/marquer_paye')
class MarquerPaiementPaye(Resource):
    @proprietaire_ns.doc(security='apikey')
    @jwt_required()
    @proprietaire_ns.marshal_with(message_model, code=200)
    @proprietaire_ns.response(400, 'Paiement déjà marqué comme payé', message_model)
    @proprietaire_ns.response(401, 'Non autorisé', message_model)
    @proprietaire_ns.response(403, 'Non autorisé à modifier ce paiement', message_model)
    @proprietaire_ns.response(404, 'Paiement non trouvé', message_model)
    @proprietaire_ns.response(500, 'Erreur interne du serveur', message_model)
    def put(self, paiement_id):
        """
        Marque un paiement spécifique comme "payé".
        """
        current_user_identity = get_jwt_identity()
        proprietaire_id = json.loads(current_user_identity)['id']

        paiement = Paiement.query.get(paiement_id)
        if not paiement:
            proprietaire_ns.abort(404, "Paiement non trouvé.")

        if not (paiement.contrat and paiement.contrat.chambre and paiement.contrat.chambre.maison and paiement.contrat.chambre.maison.proprietaire_id == proprietaire_id):
            proprietaire_ns.abort(403, "Non autorisé à modifier ce paiement.")

        if paiement.statut == 'payé':
            proprietaire_ns.abort(400, "Ce paiement est déjà marqué comme payé.")

        try:
            paiement.statut = 'payé'
            paiement.date_paiement = datetime.utcnow()
            db.session.commit()
            return {"message": "Paiement marqué comme payé avec succès!"}, 200
        except Exception as e:
            db.session.rollback()
            proprietaire_ns.abort(500, f"Erreur lors de la mise à jour du paiement: {str(e)}")

# Route pour ajouter une maison
# @proprietaire_ns.route('/maisons')



# Route pour téléverser les médias d'une chambre
@proprietaire_ns.route('/chambres/<int:chambre_id>/medias')
class ChambreMediasUpload(Resource):
    # Flask-RESTx ne gère pas directement les uploads de fichiers via marshal_with/expect de la même manière que JSON.
    # Pour la documentation, on peut utiliser reqparse ou Fields.File.
    # Pour le traitement, on continue à utiliser request.files.
    # On n'utilise PAS marshal_with car on retourne un objet Response pour les cas d'erreur partiels ou complets.
    parser = proprietaire_ns.parser()
    parser.add_argument('files', type='werkzeug.datastructures.FileStorage', location='files', required=True, action='append', help='Fichiers à téléverser')

    @proprietaire_ns.doc(security='apikey', parser=parser) # Assurez-vous que le parser est inclus pour la documentation Swagger
    @jwt_required()
    @proprietaire_ns.response(201, 'Médias téléversés avec succès', media_upload_list_response_model)
    @proprietaire_ns.response(207, 'Certains fichiers n\'ont pas pu être traités', media_upload_list_response_model)
    @proprietaire_ns.response(400, 'Aucun fichier fourni ou sélectionné / Type de fichier non autorisé', message_model)
    @proprietaire_ns.response(403, 'Accès non autorisé à cette chambre', message_model)
    @proprietaire_ns.response(404, 'Chambre non trouvée', message_model)
    @proprietaire_ns.response(500, 'Erreur interne du serveur', message_model)
    def post(self, chambre_id):
        """
        Téléverse des médias (photos) pour une chambre spécifique.
        """
        current_user_identity = get_jwt_identity()
        owner_id = json.loads(current_user_identity)['id']

        chambre = Chambre.query.get(chambre_id)
        if not chambre:
            proprietaire_ns.abort(404, "Chambre non trouvée")

        if chambre.maison.proprietaire_id != owner_id:
            proprietaire_ns.abort(403, "Vous n'êtes pas autorisé à ajouter des médias à cette chambre.")

        if 'files' not in request.files:
            proprietaire_ns.abort(400, "Aucun fichier fourni sous la clé 'files'")

        uploaded_files = request.files.getlist('files')
        if not uploaded_files or all(f.filename == '' for f in uploaded_files):
            proprietaire_ns.abort(400, "Aucun fichier sélectionné")

        uploaded_media_urls = []
        errors = []

        chambre_upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'chambres', str(chambre.id))
        os.makedirs(chambre_upload_folder, exist_ok=True)

        for file in uploaded_files:
            if file.filename == '':
                continue

            filename = secure_filename(file.filename)

            if not allowed_file(filename):
                errors.append(f"Type de fichier non autorisé pour {filename}.")
                continue

            try:
                file_path = os.path.join(chambre_upload_folder, filename)
                file.save(file_path)

                media_url = url_for('static', filename=f'uploads/chambres/{chambre.id}/{filename}', _external=True)

                new_media = Media(
                    chambre_id=chambre.id,
                    url=media_url,
                    type='photo',
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


# Route pour supprimer un média
@proprietaire_ns.route('/medias/<int:media_id>')
class MediaDeletion(Resource):
    @proprietaire_ns.doc(security='apikey')
    @jwt_required()
    @role_required(['proprietaire'])
    @proprietaire_ns.marshal_with(message_model, code=204) # 204 No Content pour une suppression réussie
    @proprietaire_ns.response(401, 'Non autorisé', message_model)
    @proprietaire_ns.response(403, 'Accès refusé', message_model)
    @proprietaire_ns.response(404, 'Média non trouvé', message_model)
    @proprietaire_ns.response(500, 'Erreur interne du serveur', message_model)
    def delete(self, media_id):
        """
        Supprime un média (photo) spécifique d'une chambre.
        """
        current_user_identity = get_jwt_identity()
        owner_id = json.loads(current_user_identity)['id']

        media = Media.query.get(media_id)
        if not media:
            proprietaire_ns.abort(404, "Média non trouvé")

        if not (media.chambre and media.chambre.maison and media.chambre.maison.proprietaire_id == owner_id):
             proprietaire_ns.abort(403, "Vous n'êtes pas autorisé à supprimer ce média.")

        try:
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
            # Pour un statut 204 No Content, on ne retourne généralement pas de corps
            # Flask-RESTx gère cela avec marshal_with(message_model, code=204)
            return {"message": "Média supprimé avec succès"}, 204
        except Exception as e:
            db.session.rollback()
            print(f"Erreur lors de la suppression du média (local): {e}")
            proprietaire_ns.abort(500, f"Erreur interne du serveur lors de la suppression du média: {str(e)}")


# Route pour approuver un contrat
@proprietaire_ns.route('/contrats/<int:contrat_id>/approuver')
class ContratApprobation(Resource):
    @proprietaire_ns.doc(security='apikey')
    @jwt_required()
    @proprietaire_ns.marshal_with(message_model, code=200)
    @proprietaire_ns.response(400, 'Le contrat n\'est pas en statut "en_attente_validation"', message_model)
    @proprietaire_ns.response(401, 'Non autorisé', message_model)
    @proprietaire_ns.response(403, 'Accès refusé', message_model)
    @proprietaire_ns.response(404, 'Contrat non trouvé', message_model)
    @proprietaire_ns.response(500, 'Erreur interne du serveur', message_model)
    def put(self, contrat_id):
        """
        Approuve un contrat de location en attente de validation, génère les paiements et marque la chambre comme indisponible.
        """
        current_user_identity = get_jwt_identity()
        current_user_id = json.loads(current_user_identity)['id']
        proprietaire = Utilisateur.query.get(current_user_id)

        if not proprietaire or proprietaire.role != 'proprietaire':
            proprietaire_ns.abort(403, "Accès refusé. Seuls les propriétaires peuvent approuver des contrats.")

        contrat = Contrat.query.get(contrat_id)
        if not contrat:
            proprietaire_ns.abort(404, "Contrat non trouvé.")

        chambre = Chambre.query.get(contrat.chambre_id)
        if not chambre or chambre.maison.proprietaire_id != proprietaire.id:
            proprietaire_ns.abort(403, "Accès refusé. Ce contrat ne vous appartient pas.")

        if contrat.statut != 'en_attente_validation':
            proprietaire_ns.abort(400, f"Le contrat n'est pas en statut 'en_attente_validation'. Statut actuel : {contrat.statut}.")

        try:
            contrat.statut = 'actif'
            db.session.add(contrat)
            db.session.flush() # Force les changements pour que contrat.id soit disponible pour les paiements

            loyer_mensuel = chambre.prix

            if contrat.montant_caution > 0:
                paiement_caution = Paiement(
                    contrat_id=contrat.id,
                    montant=contrat.montant_caution,
                    date_echeance=contrat.date_debut,
                    statut='impayé',
                )
                db.session.add(paiement_caution)

            for i in range(contrat.duree_mois):
                current_due_date = contrat.date_debut + relativedelta(months=+i)
                paiement_loyer = Paiement(
                    contrat_id=contrat.id,
                    montant=loyer_mensuel,
                    date_echeance=current_due_date,
                    statut='impayé',
                )
                db.session.add(paiement_loyer)

            chambre.disponible = False
            db.session.add(chambre)

            db.session.commit()

            return {"message": "Contrat approuvé avec succès, paiements générés et chambre marquée comme indisponible."}, 200

        except Exception as e:
            db.session.rollback()
            proprietaire_ns.abort(500, f"Une erreur est survenue lors de l'approbation du contrat: {str(e)}")


# Route pour rejeter un contrat
@proprietaire_ns.route('/contrats/<int:contrat_id>/rejeter')
class ContratRejet(Resource):
    @proprietaire_ns.doc(security='apikey')
    @jwt_required()
    @proprietaire_ns.marshal_with(message_model, code=200)
    @proprietaire_ns.response(400, 'Le contrat n\'est pas en statut "en_attente_validation"', message_model)
    @proprietaire_ns.response(401, 'Non autorisé', message_model)
    @proprietaire_ns.response(403, 'Accès refusé', message_model)
    @proprietaire_ns.response(404, 'Contrat non trouvé', message_model)
    @proprietaire_ns.response(500, 'Erreur interne du serveur', message_model)
    def put(self, contrat_id):
        """
        Rejette un contrat de location en attente de validation.
        """
        current_user_identity = get_jwt_identity()
        current_user_id = json.loads(current_user_identity)['id']
        proprietaire = Utilisateur.query.get(current_user_id)

        if not proprietaire or proprietaire.role != 'proprietaire':
            proprietaire_ns.abort(403, "Accès refusé. Seuls les propriétaires peuvent rejeter des contrats.")

        contrat = Contrat.query.get(contrat_id)
        if not contrat:
            proprietaire_ns.abort(404, "Contrat non trouvé.")

        chambre = Chambre.query.get(contrat.chambre_id)
        # Vérification basée sur la hiérarchie Maison > Proprietaire
        if not (chambre and chambre.maison and chambre.maison.proprietaire_id == proprietaire.id):
             proprietaire_ns.abort(403, "Accès refusé. Ce contrat ne vous appartient pas.")


        if contrat.statut != 'en_attente_validation':
            proprietaire_ns.abort(400, f"Le contrat n'est pas en statut 'en_attente_validation'. Statut actuel : {contrat.statut}.")

        try:
            contrat.statut = 'rejete'
            db.session.add(contrat)
            db.session.commit()
            return {"message": "Contrat rejeté avec succès."}, 200
        except Exception as e:
            db.session.rollback()
            proprietaire_ns.abort(500, f"Une erreur est survenue lors du rejet du contrat: {str(e)}")


# Route pour obtenir les demandes de location en attente
@proprietaire_ns.route('/demandes-location-en-attente')
class DemandesLocationEnAttente(Resource):
    @proprietaire_ns.doc(security='apikey')
    @jwt_required()
    @proprietaire_ns.marshal_with(demande_location_attente_model, as_list=True, code=200)
    @proprietaire_ns.response(401, 'Non autorisé', message_model)
    @proprietaire_ns.response(403, 'Accès refusé', message_model)
    @proprietaire_ns.response(500, 'Erreur interne du serveur', message_model)
    def get(self):
        """
        Récupère toutes les demandes de location (contrats en attente de validation) pour les chambres du propriétaire connecté.
        """
        current_user_identity = get_jwt_identity()
        current_user_id = json.loads(current_user_identity)['id']
        proprietaire = Utilisateur.query.get(current_user_id)

        if not proprietaire or proprietaire.role != 'proprietaire':
            proprietaire_ns.abort(403, "Accès refusé. Seuls les propriétaires peuvent voir les demandes.")

        demandes = Contrat.query.options(
            joinedload(Contrat.chambre).joinedload(Chambre.maison).joinedload(Maison.proprietaire),
            joinedload(Contrat.locataire)
        ).filter(
            Contrat.statut == 'en_attente_validation',
            Contrat.chambre.has(Chambre.maison.has(Maison.proprietaire_id == proprietaire.id))
        ).all()

        results = []
        for demande in demandes:
            locataire_nom = demande.locataire.nom_utilisateur if demande.locataire else 'N/A'
            chambre_titre = demande.chambre.titre if demande.chambre else 'N/A'

            results.append({
                "id": demande.id,
                "locataire_id": demande.locataire.id,
                "locataire_nom": locataire_nom,
                "chambre_id": demande.chambre.id,
                "chambre_titre": chambre_titre,
                "date_debut": demande.date_debut.isoformat(),
                "date_fin": demande.date_fin.isoformat(),
                "montant_caution": float(demande.montant_caution),
                "duree_mois": demande.duree_mois,
                "statut": demande.statut
            })
        return results, 200