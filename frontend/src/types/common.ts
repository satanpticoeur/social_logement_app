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

// frontend/src/types/common.ts

// ... (autres interfaces) ...

export interface Contrat {
    id: number;
    chambre_id: number;
    locataire_id: number;
    date_debut: string;
    date_fin: string;
    description: string | null;
    montant_caution: string; // Ou number si tu gères la conversion côté backend
    mois_caution: number;
    periodicite: string;
    mode_paiement: string;
    statut: string;
    cree_le: string;
    chambre?: Chambre; // Optionnel si non toujours inclus
    locataire?: Utilisateur; // Optionnel si non toujours inclus
    total_expected_amount?: number; // <-- AJOUTE CETTE LIGNE
    total_paid_amount?: number;     // <-- AJOUTE CETTE LIGNE
    remaining_balance?: number;     // <-- AJOUTE CETTE LIGNE
}


export interface Paiement {
    id: number;
    contrat_id: number;
    montant: number;
    date_echeance: string;
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

// type ErrorResponse

export interface ErrorResponse {
    status: number;
    message: string;
    details?: string; // Optionnel pour des informations supplémentaires
}