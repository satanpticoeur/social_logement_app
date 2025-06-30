from app import db
from datetime import datetime

class Utilisateur(db.Model):
    __tablename__ = 'utilisateurs' # Spécifie le nom de la table SQL
    id = db.Column(db.Integer, primary_key=True)
    nom_utilisateur = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True, nullable=False) # L'email doit être unique et non nul
    telephone = db.Column(db.String(255))
    cni = db.Column(db.String(255))
    role = db.Column(db.String(255)) # 'proprietaire' | 'locataire'
    cree_le = db.Column(db.DateTime, default=datetime.utcnow) # Utilise datetime.utcnow pour un timestamp

    # Relations
    maisons = db.relationship('Maison', backref='proprietaire', lazy=True)
    contrats_locataire = db.relationship('Contrat', backref='locataire', lazy=True, foreign_keys='Contrat.locataire_id')
    rendez_vous_locataire = db.relationship('RendezVous', backref='locataire', lazy=True, foreign_keys='RendezVous.locataire_id')
    problemes_signales = db.relationship('Probleme', backref='signale_par_utilisateur', lazy=True, foreign_keys='Probleme.signale_par')


    def __repr__(self):
        return f'<Utilisateur {self.nom_utilisateur} ({self.role})>'

class Maison(db.Model):
    __tablename__ = 'maisons'
    id = db.Column(db.Integer, primary_key=True)
    proprietaire_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), nullable=False)
    adresse = db.Column(db.String(255))
    latitude = db.Column(db.Numeric(10, 8)) # Précision pour la latitude/longitude
    longitude = db.Column(db.Numeric(11, 8)) # Précision pour la latitude/longitude
    description = db.Column(db.Text)
    cree_le = db.Column(db.DateTime, default=datetime.utcnow)

    # Relation
    chambres = db.relationship('Chambre', backref='maison', lazy=True)

    def __repr__(self):
        return f'<Maison {self.adresse}>'

class Chambre(db.Model):
    __tablename__ = 'chambres'
    id = db.Column(db.Integer, primary_key=True)
    maison_id = db.Column(db.Integer, db.ForeignKey('maisons.id'), nullable=False)
    titre = db.Column(db.String(255))
    description = db.Column(db.Text)
    taille = db.Column(db.String(255)) # ex: '12m²'
    type = db.Column(db.String(255)) # 'simple' | 'appartement' | 'maison'
    meublee = db.Column(db.Boolean)
    salle_de_bain = db.Column(db.Boolean)
    prix = db.Column(db.Numeric(10, 2)) # Précision pour le prix (ex: 1234.50)
    disponible = db.Column(db.Boolean, default=True) # Par défaut, une chambre est disponible
    cree_le = db.Column(db.DateTime, default=datetime.utcnow)

    # Relations
    contrats = db.relationship('Contrat', backref='chambre', lazy=True)
    rendez_vous = db.relationship('RendezVous', backref='chambre', lazy=True)
    medias = db.relationship('Media', backref='chambre', lazy=True)

    def __repr__(self):
        return f'<Chambre {self.titre} (Maison ID: {self.maison_id})>'

# Ajoute les autres modèles ici, en te basant sur le script SQL :
# Contrat, Paiement, RendezVous, Media, Probleme

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

    # Relations
    paiements = db.relationship('Paiement', backref='contrat', lazy=True)
    problemes = db.relationship('Probleme', backref='contrat', lazy=True)

    def __repr__(self):
        return f'<Contrat {self.id} - Locataire: {self.locataire_id} - Chambre: {self.chambre_id}>'

class Paiement(db.Model):
    __tablename__ = 'paiements'
    id = db.Column(db.Integer, primary_key=True)
    contrat_id = db.Column(db.Integer, db.ForeignKey('contrats.id'), nullable=False)
    montant = db.Column(db.Numeric(10, 2))
    statut = db.Column(db.String(255)) # 'payé' | 'impayé'
    date_echeance = db.Column(db.Date)
    date_paiement = db.Column(db.DateTime) # Peut être null si impayé
    cree_le = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Paiement {self.id} - Contrat: {self.contrat_id} - Montant: {self.montant}>'

class RendezVous(db.Model):
    __tablename__ = 'rendez_vous'
    id = db.Column(db.Integer, primary_key=True)
    locataire_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), nullable=False)
    chambre_id = db.Column(db.Integer, db.ForeignKey('chambres.id'), nullable=False)
    date_heure = db.Column(db.DateTime)
    statut = db.Column(db.String(255)) # 'en_attente' | 'confirmé' | 'annulé'
    cree_le = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<RendezVous {self.id} - Locataire: {self.locataire_id} - Chambre: {self.chambre_id}>'

class Media(db.Model):
    __tablename__ = 'medias'
    id = db.Column(db.Integer, primary_key=True)
    chambre_id = db.Column(db.Integer, db.ForeignKey('chambres.id'), nullable=False)
    url = db.Column(db.String(255))
    type = db.Column(db.String(255)) # 'photo' | 'video'
    description = db.Column(db.Text)
    cree_le = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Media {self.id} - Chambre: {self.chambre_id} - Type: {self.type}>'

class Probleme(db.Model):
    __tablename__ = 'problemes'
    id = db.Column(db.Integer, primary_key=True)
    contrat_id = db.Column(db.Integer, db.ForeignKey('contrats.id'), nullable=False)
    signale_par = db.Column(db.Integer, db.ForeignKey('utilisateurs.id')) # Utilisateur qui a signalé
    description = db.Column(db.Text)
    type = db.Column(db.String(255)) # 'plomberie' | 'electricite' | 'autre'
    responsable = db.Column(db.String(255)) # 'locataire' | 'proprietaire'
    resolu = db.Column(db.Boolean, default=False) # Par défaut, un problème n'est pas résolu
    cree_le = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Probleme {self.id} - Contrat: {self.contrat_id} - Type: {self.type}>'