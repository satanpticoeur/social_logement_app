export interface Utilisateur {
    id: number;
    nom_utilisateur: string;
    email: string;
    telephone: string | null;
    cni: string | null;
    role: string;
    cree_le: string; // ISO format date string
}

export interface Maison {
    id: number;
    proprietaire_id: number;
    adresse: string;
    latitude: string | null;
    longitude: string | null;
    description: string | null;
    cree_le: string;
    proprietaire?: Utilisateur; // Peut être inclus lors de la sérialisation
}

export interface Chambre {
    id: number;
    maison_id: number;
    titre: string;
    description: string | null;
    taille: string;
    type: 'simple' | 'appartement' | 'maison';
    meublee: boolean;
    salle_de_bain: boolean;
    prix: string; // Garder comme string si Decimal de Python est renvoyé
    disponible: boolean;
    cree_le: string;
    maison?: Maison; // Peut être inclus
    medias?: Media[]; // Peut être inclus
}

export interface Contrat {
    id: number;
    locataire_id: number;
    chambre_id: number;
    date_debut: string;
    date_fin: string;
    montant_caution: string;
    mois_caution: number | null;
    description: string | null;
    mode_paiement: string;
    periodicite: 'journalier' | 'hebdomadaire' | 'mensuel';
    statut: string;
    cree_le: string;
}

export interface Paiement {
    id: number;
    contrat_id: number;
    montant: string;
    statut: 'payé' | 'impayé';
    date_echeance: string;
    date_paiement: string | null;
    cree_le: string;
}

export interface RendezVous {
    id: number;
    locataire_id: number;
    chambre_id: number;
    date_heure: string;
    statut: 'en_attente' | 'confirmé' | 'annulé';
    cree_le: string;
}

export interface Media {
    id: number;
    chambre_id: number;
    url: string;
    type: 'photo' | 'video';
    description: string | null;
    cree_le: string;
}