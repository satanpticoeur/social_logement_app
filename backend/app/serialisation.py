
def serialize_utilisateur(utilisateur):
    if not utilisateur:
        return None
    return {
        "id": utilisateur.id,
        "nom_utilisateur": utilisateur.nom_utilisateur,
        "email": utilisateur.email,
        "telephone": utilisateur.telephone,
        "cni": utilisateur.cni,
        "role": utilisateur.role,
        "cree_le": utilisateur.cree_le.isoformat() if utilisateur.cree_le else None,
    }


def serialize_maison(maison):
    if not maison:
        return None
    return {
        "id": maison.id,
        "proprietaire_id": maison.proprietaire_id,
        "adresse": maison.adresse,
        "ville": maison.ville,
        "description": maison.description,
        "cree_le": maison.cree_le.isoformat() if maison.cree_le else None,
        # Inclure le propriétaire si joint par joinedload
        "proprietaire": serialize_utilisateur(maison.proprietaire) if hasattr(maison, 'proprietaire') else None
    }


def serialize_media(media):
    if not media:
        return None
    return {
        "id": media.id,
        "chambre_id": media.chambre_id,
        "url": media.url,
        "type": media.type,
        "description": media.description,
        "cree_le": media.cree_le.isoformat() if media.cree_le else None,
    }


def serialize_contrat(contrat):
    if not contrat:
        return None
    return {
        "id": contrat.id,
        "locataire_id": contrat.locataire_id,
        "chambre_id": contrat.chambre_id,
        "date_debut": contrat.date_debut.isoformat() if contrat.date_debut else None,
        "date_fin": contrat.date_fin.isoformat() if contrat.date_fin else None,
        "montant_caution": str(contrat.montant_caution) if contrat.montant_caution is not None else None,
        # Convertir Decimal en str
        "mois_caution": contrat.mois_caution,
        "description": contrat.description,  # Nouveau champ
        "mode_paiement": contrat.mode_paiement,  # Nouveau champ
        "periodicite": contrat.periodicite,  # Nouveau champ
        "statut": contrat.statut,  # Nouveau champ
        "cree_le": contrat.cree_le.isoformat() if contrat.cree_le else None,
        # Inclure les relations chargées par joinedload
        "locataire": serialize_utilisateur(contrat.locataire) if hasattr(contrat, 'locataire') else None,
        "chambre": serialize_chambre(contrat.chambre) if hasattr(contrat, 'chambre') else None
    }


def serialize_chambre(chambre):
    if not chambre:
        return None
    return {
        "id": chambre.id,
        "maison_id": chambre.maison_id,
        "titre": chambre.titre,
        "description": chambre.description,
        "taille": chambre.taille,
        "type": chambre.type,
        "meublee": chambre.meublee,
        "salle_de_bain": chambre.salle_de_bain,
        "prix": str(chambre.prix) if chambre.prix is not None else None,  # Convertir Decimal en str
        "disponible": chambre.disponible,
        "cree_le": chambre.cree_le.isoformat() if chambre.cree_le else None,
        # Inclure la maison et les médias si joints
        "maison": serialize_maison(chambre.maison) if hasattr(chambre, 'maison') else None,
        "medias": [serialize_media(m) for m in chambre.medias] if hasattr(chambre, 'medias') and chambre.medias else []
    }


def serialize_paiement(paiement):
    if not paiement:
        return None
    return {
        "id": paiement.id,
        "contrat_id": paiement.contrat_id,
        "montant": str(paiement.montant) if paiement.montant is not None else None,  # Convertir Decimal en str
        "date_paiement": paiement.date_paiement.isoformat() if paiement.date_paiement else None,
        "statut": paiement.statut,
        "cree_le": paiement.cree_le.isoformat() if paiement.cree_le else None,
        # Inclure le contrat si joint par joinedload
        "contrat": serialize_contrat(paiement.contrat) if hasattr(paiement, 'contrat') else None
    }


def serialize_rendez_vous(rdv):
    if not rdv:
        return None
    return {
        "id": rdv.id,
        "locataire_id": rdv.locataire_id,
        "chambre_id": rdv.chambre_id,
        "date_heure": rdv.date_heure.isoformat() if rdv.date_heure else None,
        "statut": rdv.statut,
        "cree_le": rdv.cree_le.isoformat() if rdv.cree_le else None,
        "locataire": serialize_utilisateur(rdv.locataire) if hasattr(rdv, 'locataire') else None,
        "chambre": serialize_chambre(rdv.chambre) if hasattr(rdv, 'chambre') else None,
    }


def serialize_probleme(probleme):
    if not probleme:
        return None
    return {
        "id": probleme.id,
        "contrat_id": probleme.contrat_id,
        "signale_par": probleme.signale_par,
        "description": probleme.description,
        "type": probleme.type,
        "responsable": probleme.responsable,
        "resolu": probleme.resolu,
        "cree_le": probleme.cree_le.isoformat() if probleme.cree_le else None,
        "contrat": serialize_contrat(probleme.contrat) if hasattr(probleme, 'contrat') else None,
    }