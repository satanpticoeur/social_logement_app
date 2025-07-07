from . import db, bcrypt


class Utilisateur(db.Model):
    __tablename__ = 'utilisateurs'  # Nom de table explicite au pluriel
    id = db.Column(db.Integer, primary_key=True)
    nom_utilisateur = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    mot_de_passe = db.Column(db.String(128), nullable=False)
    telephone = db.Column(db.String(20), nullable=True)
    cni = db.Column(db.String(50), unique=True, nullable=True)
    role = db.Column(db.String(20), nullable=False, default='locataire')  # 'proprietaire', 'locataire', 'admin'
    cree_le = db.Column(db.DateTime,
                        default=db.func.current_timestamp())  # Utilise db.func.current_timestamp() pour la BD

    # Relations : Utilisation de `back_populates` pour les relations bidirectionnelles.
    # Il faut que le nom du `backref` dans la classe opposée corresponde à ce nom.
    maisons = db.relationship('Maison', back_populates='proprietaire', lazy=True)
    contrats_locataire = db.relationship('Contrat', back_populates='locataire', lazy=True)  # Renommé pour clarté
    rendez_vous_locataire = db.relationship('RendezVous', back_populates='locataire',
                                            lazy=True)  # Ajouté pour la relation RendezVous
    problemes_signales = db.relationship('Probleme', back_populates='signale_par_utilisateur', lazy=True,
                                         foreign_keys='Probleme.signale_par')  # Ajouté pour la relation Probleme

    def __repr__(self):
        return f'<Utilisateur {self.nom_utilisateur}>'

    def set_password(self, password):
        self.mot_de_passe = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.mot_de_passe, password)


class Maison(db.Model):
    __tablename__ = 'maisons'  # Nom de table explicite au pluriel
    id = db.Column(db.Integer, primary_key=True)
    adresse = db.Column(db.String(200), nullable=False)
    ville = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    nombre_chambres = db.Column(db.Integer, default=0)
    cree_le = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Clé étrangère pointant vers 'utilisateurs.id' (conforme à __tablename__ d'Utilisateur)
    proprietaire_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), nullable=False)

    # Relations
    # Utilisation de `back_populates` pour la relation bidirectionnelle avec Utilisateur
    proprietaire = db.relationship('Utilisateur', back_populates='maisons')
    chambres = db.relationship('Chambre', back_populates='maison', lazy=True)

    def __repr__(self):
        return f'<Maison {self.adresse}>'


class Chambre(db.Model):
    __tablename__ = 'chambres'  # Nom de table explicite au pluriel
    id = db.Column(db.Integer, primary_key=True)
    maison_id = db.Column(db.Integer, db.ForeignKey('maisons.id'), nullable=False)
    titre = db.Column(db.String(255), nullable=False)  # Rendu non nullable car c'est un titre
    description = db.Column(db.Text, nullable=True)  # Peut être nullable
    taille = db.Column(db.String(255), nullable=True)  # ex: 12m², peut être nullable
    type = db.Column(db.String(255), nullable=True)  # 'simple' | 'appartement' | 'maison', peut être nullable
    meublee = db.Column(db.Boolean, default=False)  # Valeur par défaut
    salle_de_bain = db.Column(db.Boolean, default=False)  # Valeur par défaut
    prix = db.Column(db.Numeric(10, 2), nullable=False)  # Prix doit être obligatoire
    disponible = db.Column(db.Boolean, default=True)  # Valeur par défaut
    cree_le = db.Column(db.DateTime, default=db.func.current_timestamp())  # Utilise db.func.current_timestamp()

    # Relations : Utilisation de back_populates pour la clarté bidirectionnelle
    maison = db.relationship('Maison', back_populates='chambres')
    contrats_chambre = db.relationship('Contrat', back_populates='chambre', lazy=True)
    rendez_vous = db.relationship('RendezVous', back_populates='chambre', lazy=True)
    medias = db.relationship('Media', back_populates='chambre', lazy=True)

    def __repr__(self):
        return f'<Chambre {self.titre}>'


class Contrat(db.Model):
    __tablename__ = 'contrats'  # Nom de table explicite au pluriel
    id = db.Column(db.Integer, primary_key=True)
    # Clés étrangères pointant vers 'utilisateurs.id' et 'chambres.id'
    locataire_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), nullable=False)
    chambre_id = db.Column(db.Integer, db.ForeignKey('chambres.id'), nullable=False)
    date_debut = db.Column(db.Date, nullable=False)  # La date de début est obligatoire
    date_fin = db.Column(db.Date, nullable=False)  # La date de fin est obligatoire
    montant_caution = db.Column(db.Numeric(10, 2), nullable=True)  # Peut être nullable
    mois_caution = db.Column(db.Integer, nullable=True)  # <= 3, peut être nullable
    description = db.Column(db.Text, nullable=True)  # Peut être nullable
    mode_paiement = db.Column(db.String(255), nullable=False, default='virement')  # Le mode de paiement est important
    periodicite = db.Column(db.String(255), nullable=False,
                            default='mensuel')  # 'journalier' | 'hebdomadaire' | 'mensuel'
    statut = db.Column(db.String(255), nullable=False, default='actif')  # 'actif' | 'resilié'
    cree_le = db.Column(db.DateTime, default=db.func.current_timestamp())  # Utilise db.func.current_timestamp()

    # Relations : Utilisation de back_populates pour une clarté bidirectionnelle
    locataire = db.relationship('Utilisateur', back_populates='contrats_locataire')
    chambre = db.relationship('Chambre', back_populates='contrats_chambre')
    paiements = db.relationship('Paiement', back_populates='contrat', lazy=True)
    problemes = db.relationship('Probleme', back_populates='contrat', lazy=True)

    def __repr__(self):
        return f'<Contrat {self.id}>'


class Paiement(db.Model):
    __tablename__ = 'paiements'  # Nom de table explicite au pluriel
    id = db.Column(db.Integer, primary_key=True)
    contrat_id = db.Column(db.Integer, db.ForeignKey('contrats.id'), nullable=False)
    montant = db.Column(db.Numeric(10, 2), nullable=False)  # Montant doit être obligatoire
    date_echeance = db.Column(db.Date, nullable=False)  # Date d'échéance obligatoire
    date_paiement = db.Column(db.DateTime, nullable=True)  # Peut être nullable si non encore payé
    statut = db.Column(db.String(255), nullable=False,
                       default='impayé')  # 'payé' | 'impayé' | 'partiel', statut obligatoire
    cree_le = db.Column(db.DateTime, default=db.func.current_timestamp())  # Utilise db.func.current_timestamp()

    # Relation inverse du contrat
    contrat = db.relationship('Contrat', back_populates='paiements')

    def __repr__(self):
        return f'<Paiement {self.montant} pour Contrat {self.contrat_id}>'


class RendezVous(db.Model):
    __tablename__ = 'rendez_vous'  # Nom de table explicite au pluriel
    id = db.Column(db.Integer, primary_key=True)
    # Clés étrangères pointant vers 'utilisateurs.id' et 'chambres.id'
    locataire_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), nullable=False)
    chambre_id = db.Column(db.Integer, db.ForeignKey('chambres.id'), nullable=False)
    date_heure = db.Column(db.DateTime, nullable=False)  # Date et heure du RDV sont obligatoires
    statut = db.Column(db.String(255), nullable=False, default='en_attente')  # 'en_attente' | 'confirme' | 'annule'
    cree_le = db.Column(db.DateTime, default=db.func.current_timestamp())  # Utilise db.func.current_timestamp()

    # Relations
    locataire = db.relationship('Utilisateur',
                                back_populates='rendez_vous_locataire')  # Met à jour le back_populates pour correspondre à Utilisateur
    chambre = db.relationship('Chambre', back_populates='rendez_vous')

    def __repr__(self):
        return f'<RendezVous {self.id}>'


class Media(db.Model):
    __tablename__ = 'medias'  # Nom de table explicite au pluriel
    id = db.Column(db.Integer, primary_key=True)
    chambre_id = db.Column(db.Integer, db.ForeignKey('chambres.id'), nullable=False)
    url = db.Column(db.String(255), nullable=False)  # L'URL doit être obligatoire
    type = db.Column(db.String(255), nullable=True)  # 'photo' | 'video', peut être nullable
    description = db.Column(db.Text, nullable=True)  # Peut être nullable
    cree_le = db.Column(db.DateTime, default=db.func.current_timestamp())  # Utilise db.func.current_timestamp()

    # Relation
    chambre = db.relationship('Chambre', back_populates='medias')

    def __repr__(self):
        return f'<Media {self.url}>'


class Probleme(db.Model):
    __tablename__ = 'problemes'  # Nom de table explicite au pluriel
    id = db.Column(db.Integer, primary_key=True)
    contrat_id = db.Column(db.Integer, db.ForeignKey('contrats.id'), nullable=False)
    # Clé étrangère pointant vers 'utilisateurs.id'
    signale_par = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), nullable=False)  # L'utilisateur qui a signalé
    description = db.Column(db.Text, nullable=False)  # La description du problème est obligatoire
    type = db.Column(db.String(255), nullable=False)  # 'plomberie' | 'electricite' | 'autre', type obligatoire
    responsable = db.Column(db.String(255), nullable=True)  # 'locataire' | 'proprietaire', peut être nullable
    resolu = db.Column(db.Boolean, default=False)  # Par défaut, un problème n'est pas résolu
    cree_le = db.Column(db.DateTime, default=db.func.current_timestamp())  # Utilise db.func.current_timestamp()

    # Relations
    contrat = db.relationship('Contrat', back_populates='problemes')
    # `foreign_keys=[signale_par]` est correct ici car il y a deux relations entre Probleme et Utilisateur
    signale_par_utilisateur = db.relationship('Utilisateur', back_populates='problemes_signales',
                                              foreign_keys=[signale_par])

    def __repr__(self):
        return f'<Probleme {self.id}>'
