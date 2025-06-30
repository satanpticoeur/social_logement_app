export interface Utilisateur {
    id: number;
    nom_utilisateur: string;
    email: string;
    telephone?: string;
    cni?: string;
    role: 'proprietaire' | 'locataire';
    cree_le: string; // Date au format ISO string
}

export interface Maison {
    id: number;
    proprietaire_id: number;
    adresse: string;
    latitude?: number;
    longitude?: number;
    description?: string;
    cree_le: string;
    proprietaire?: Utilisateur; // Peut être inclus si ton API le joint
}

export interface Media {
    id: number;
    chambre_id: number;
    url: string;
    type: 'photo' | 'video';
    description?: string;
    cree_le: string;
}

export interface Chambre {
    id: number;
    maison_id: number;
    titre: string;
    description?: string;
    taille?: string;
    type: 'simple' | 'appartement' | 'maison';
    meublee: boolean;
    salle_de_bain: boolean;
    prix: number; // Assumons que le prix est un nombre si ton API le renvoie comme tel
    disponible: boolean;
    cree_le: string;
    maison?: Maison; // Peut être inclus si ton API le joint
    medias?: Media[]; // Peut être inclus si ton API le joint
}

export interface Contrat {
    id: number;
    locataire_id: number;
    chambre_id: number;
    date_debut: string; // Date au format ISO string (ex: "YYYY-MM-DD")
    date_fin: string;   // Date au format ISO string (ex: "YYYY-MM-DD")
    montant_caution: number; // Ou 'string' si ton backend sérialise Decimal en string
    mois_caution: number;
    description?: string; // Ajouté
    mode_paiement?: string; // Ajouté
    periodicite: 'journalier' | 'hebdomadaire' | 'mensuel'; // Renommé et type mis à jour
    statut: 'actif' | 'resilié'; // Ajouté
    cree_le: string; // Date au format ISO string
    locataire?: Utilisateur; // Doit être présent si joinedload est utilisé
    chambre?: Chambre; // Doit être présent si joinedload est utilisé
}

export interface Paiement {
    id: number;
    contrat_id: number;
    montant: number;
    date_paiement: string; // Date au format ISO string
    statut: 'payé' | 'impayé' | 'partiel';
    cree_le: string;
    contrat?: Contrat; // Peut être inclus si ton API le joint (très utile ici)
}

export interface RendezVous {
    id: number;
    locataire_id: number;
    chambre_id: number;
    date_heure: string; // Date et heure au format ISO string
    statut: 'en_attente' | 'confirme' | 'annule';
    cree_le: string;
    locataire?: Utilisateur;
    chambre?: Chambre;
}

export interface Probleme {
    id: number;
    contrat_id: number;
    signale_par: number;
    description: string;
    type: 'plomberie' | 'electricite' | 'autre';
    responsable: 'locataire' | 'proprietaire';
    resolu: boolean;
    cree_le: string;
    contrat?: Contrat;
}