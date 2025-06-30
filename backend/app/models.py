# backend/models.py

from datetime import datetime
from . import db # Assure-toi que db est bien importé de ton __init__.py

class Utilisateur(db.Model):
    __tablename__ = 'utilisateurs'
    id = db.Column(db.Integer, primary_key=True)
    nom_utilisateur = db.Column(db.String(255))
    email = db.Column(db.String(255))
    telephone = db.Column(db.String(255))
    cni = db.Column(db.String(255))
    role = db.Column(db.String(255)) # 'proprietaire' | 'locataire'
    cree_le = db.Column(db.DateTime, default=datetime.utcnow)

    # Relations où Utilisateur est le parent ou est lié
    maisons = db.relationship('Maison', back_populates='proprietaire', lazy=True)
    contrats_locataire = db.relationship('Contrat', back_populates='locataire', lazy=True)
    rendez_vous = db.relationship('RendezVous', back_populates='locataire', lazy=True)
    problemes_signales = db.relationship('Probleme', back_populates='signale_par_utilisateur', lazy=True)


class Maison(db.Model):
    __tablename__ = 'maisons'
    id = db.Column(db.Integer, primary_key=True)
    proprietaire_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), nullable=False)
    adresse = db.Column(db.String(255))
    latitude = db.Column(db.Numeric)
    longitude = db.Column(db.Numeric)
    description = db.Column(db.Text)
    cree_le = db.Column(db.DateTime, default=datetime.utcnow)

    # Relations
    proprietaire = db.relationship('Utilisateur', back_populates='maisons')
    chambres = db.relationship('Chambre', back_populates='maison', lazy=True)


class Chambre(db.Model):
    __tablename__ = 'chambres'
    id = db.Column(db.Integer, primary_key=True)
    maison_id = db.Column(db.Integer, db.ForeignKey('maisons.id'), nullable=False)
    titre = db.Column(db.String(255))
    description = db.Column(db.Text)
    taille = db.Column(db.String(255)) # ex: 12m²
    type = db.Column(db.String(255)) # 'simple' | 'appartement' | 'maison'
    meublee = db.Column(db.Boolean)
    salle_de_bain = db.Column(db.Boolean)
    prix = db.Column(db.Numeric)
    disponible = db.Column(db.Boolean)
    cree_le = db.Column(db.DateTime, default=datetime.utcnow)

    # Relations
    maison = db.relationship('Maison', back_populates='chambres')
    contrats_chambre = db.relationship('Contrat', back_populates='chambre', lazy=True)
    rendez_vous = db.relationship('RendezVous', back_populates='chambre', lazy=True)
    medias = db.relationship('Media', back_populates='chambre', lazy=True)


class Contrat(db.Model):
    __tablename__ = 'contrats'
    id = db.Column(db.Integer, primary_key=True)
    locataire_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), nullable=False)
    chambre_id = db.Column(db.Integer, db.ForeignKey('chambres.id'), nullable=False)
    date_debut = db.Column(db.Date)
    date_fin = db.Column(db.Date)
    montant_caution = db.Column(db.Numeric(10, 2))
    mois_caution = db.Column(db.Integer) # <= 3
    description = db.Column(db.Text)
    mode_paiement = db.Column(db.String(255)) # 'virement' | 'cash' | 'mobile money'
    periodicite = db.Column(db.String(255)) # 'journalier' | 'hebdomadaire' | 'mensuel'
    statut = db.Column(db.String(255)) # 'actif' | 'resilié'
    cree_le = db.Column(db.DateTime, default=datetime.utcnow)

    # Relations : Utilisation de back_populates pour une clarté bidirectionnelle
    locataire = db.relationship('Utilisateur', back_populates='contrats_locataire')
    chambre = db.relationship('Chambre', back_populates='contrats_chambre')

    # Paiements et Problèmes aussi en back_populates pour éviter les conflits
    paiements = db.relationship('Paiement', back_populates='contrat', lazy=True)
    problemes = db.relationship('Probleme', back_populates='contrat', lazy=True)


class Paiement(db.Model):
    __tablename__ = 'paiements'
    id = db.Column(db.Integer, primary_key=True)
    contrat_id = db.Column(db.Integer, db.ForeignKey('contrats.id'), nullable=False)
    montant = db.Column(db.Numeric(10, 2))
    date_paiement = db.Column(db.DateTime)
    statut = db.Column(db.String(255)) # 'payé' | 'impayé' | 'partiel'
    cree_le = db.Column(db.DateTime, default=datetime.utcnow)

    # Relation inverse du contrat
    contrat = db.relationship('Contrat', back_populates='paiements')


class RendezVous(db.Model):
    __tablename__ = 'rendez_vous'
    id = db.Column(db.Integer, primary_key=True)
    locataire_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), nullable=False)
    chambre_id = db.Column(db.Integer, db.ForeignKey('chambres.id'), nullable=False)
    date_heure = db.Column(db.DateTime)
    statut = db.Column(db.String(255)) # 'en_attente' | 'confirme' | 'annule'
    cree_le = db.Column(db.DateTime, default=datetime.utcnow)

    # Relations
    locataire = db.relationship('Utilisateur', back_populates='rendez_vous')
    chambre = db.relationship('Chambre', back_populates='rendez_vous')


class Media(db.Model):
    __tablename__ = 'medias'
    id = db.Column(db.Integer, primary_key=True)
    chambre_id = db.Column(db.Integer, db.ForeignKey('chambres.id'), nullable=False)
    url = db.Column(db.String(255))
    type = db.Column(db.String(255)) # 'photo' | 'video'
    description = db.Column(db.Text)
    cree_le = db.Column(db.DateTime, default=datetime.utcnow)

    # Relation
    chambre = db.relationship('Chambre', back_populates='medias')


class Probleme(db.Model):
    __tablename__ = 'problemes'
    id = db.Column(db.Integer, primary_key=True)
    contrat_id = db.Column(db.Integer, db.ForeignKey('contrats.id'), nullable=False)
    signale_par = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), nullable=False) # L'utilisateur qui a signalé
    description = db.Column(db.Text)
    type = db.Column(db.String(255)) # 'plomberie' | 'electricite' | 'autre'
    responsable = db.Column(db.String(255)) # 'locataire' | 'proprietaire'
    resolu = db.Column(db.Boolean)
    cree_le = db.Column(db.DateTime, default=datetime.utcnow)

    # Relations
    contrat = db.relationship('Contrat', back_populates='problemes') # Relation Contrat <-> Probleme
    signale_par_utilisateur = db.relationship('Utilisateur', back_populates='problemes_signales', foreign_keys=[signale_par]) # Lien vers l'utilisateur qui a signalé