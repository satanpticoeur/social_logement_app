import React from 'react';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
    DialogTrigger // Toujours utile si le déclencheur est encapsulé
} from "@/components/ui/dialog";
import { ScrollArea } from "@/components/ui/scroll-area";
import {EyeIcon} from "lucide-react";
import {Button} from "@/components/ui/button.tsx";

// Définissez l'interface Chambre exactement comme elle est reçue de votre API pour les détails
interface ChambreDetails {
    id: number;
    maison_id: number;
    titre: string;
    description: string | null;
    taille: string | null;
    type: string | null;
    meublee: boolean;
    salle_de_bain: boolean;
    prix: number;
    disponible: boolean;
    // Ajoutez ici d'autres champs de détails si votre API les fournit (ex: date de création, etc.)
    adresse_maison: string; // Utile pour l'affichage des détails
    ville_maison?: string; // Utile pour l'affichage des détails
    contrats_actifs: Array<{
        contrat_id: number;
        locataire_nom_utilisateur: string;
        date_debut: string;
        date_fin: string;
        statut: string;
    }>;
    medias?: Array<{
        id: number;
        url: string;
        type: string; // Ex: 'image', 'video', etc.
        description?: string;
    }>;
}

interface RoomDetailsDialogProps {
    chambre: ChambreDetails; // La chambre dont on veut afficher les détails
}

const RoomDetailsDialog: React.FC<RoomDetailsDialogProps> = ({ chambre }) => {
    return (
        <Dialog>
            <DialogTrigger asChild>
                <Button variant={"secondary"} size={"sm"}>
                    <EyeIcon/>
                </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[425px] md:max-w-[600px] lg:max-w-[700px]">
                <DialogHeader>
                    <DialogTitle>Détails de la Chambre: {chambre.titre}</DialogTitle>
                    <DialogDescription>
                        Informations complètes sur la chambre.
                    </DialogDescription>
                </DialogHeader>
                <ScrollArea className="max-h-[70vh] py-4">
                    <div className="grid gap-4 py-2">
                        <div className="grid grid-cols-3 items-center gap-4">
                            <span className="text-sm font-medium text-gray-700">Maison:</span>
                            <span className="col-span-2 text-sm">{chambre.adresse_maison}, {chambre.ville_maison}</span>
                        </div>
                        <div className="grid grid-cols-3 items-center gap-4">
                            <span className="text-sm font-medium text-gray-700">Titre:</span>
                            <span className="col-span-2 text-sm">{chambre.titre}</span>
                        </div>
                        <div className="grid grid-cols-3 items-center gap-4">
                            <span className="text-sm font-medium text-gray-700">Description:</span>
                            <span className="col-span-2 text-sm">{chambre.description || 'Non spécifiée'}</span>
                        </div>
                        <div className="grid grid-cols-3 items-center gap-4">
                            <span className="text-sm font-medium text-gray-700">Taille:</span>
                            <span className="col-span-2 text-sm">{chambre.taille || 'Non spécifiée'}</span>
                        </div>
                        <div className="grid grid-cols-3 items-center gap-4">
                            <span className="text-sm font-medium text-gray-700">Type:</span>
                            <span className="col-span-2 text-sm">{chambre.type || 'Non spécifié'}</span>
                        </div>
                        <div className="grid grid-cols-3 items-center gap-4">
                            <span className="text-sm font-medium text-gray-700">Meublée:</span>
                            <span className="col-span-2 text-sm">{chambre.meublee ? 'Oui' : 'Non'}</span>
                        </div>
                        <div className="grid grid-cols-3 items-center gap-4">
                            <span className="text-sm font-medium text-gray-700">Salle de bain privée:</span>
                            <span className="col-span-2 text-sm">{chambre.salle_de_bain ? 'Oui' : 'Non'}</span>
                        </div>
                        <div className="grid grid-cols-3 items-center gap-4">
                            <span className="text-sm font-medium text-gray-700">Prix:</span>
                            <span className="col-span-2 text-sm font-bold">{chambre.prix.toLocaleString('fr-SN', { style: 'currency', currency: 'XOF' })}</span>
                        </div>
                        <div className="grid grid-cols-3 items-center gap-4">
                            <span className="text-sm font-medium text-gray-700">Disponibilité:</span>
                            <span className="col-span-2 text-sm">{chambre.disponible ? 'Disponible' : 'Non disponible'}</span>
                        </div>

                        {chambre.contrats_actifs && chambre.contrats_actifs.length > 0 && (
                            <div className="mt-4 border-t pt-3">
                                <h4 className="text-md font-semibold text-gray-800 mb-2">Contrats Actifs :</h4>
                                {chambre.contrats_actifs.map(contrat => (
                                    <div key={contrat.contrat_id} className="text-sm text-gray-700 mb-1 pl-2 border-l-2 border-gray-200">
                                        <p>Locataire: <span className="font-medium">{contrat.locataire_nom_utilisateur}</span></p>
                                        <p>Du: <span className="font-medium">{contrat.date_debut}</span> Au: <span className="font-medium">{contrat.date_fin}</span></p>
                                        <p>Statut: <span className="font-medium">{contrat.statut}</span></p>
                                    </div>
                                ))}
                            </div>
                        )}
                        {chambre.medias && chambre.medias.length > 0 && (
                            <div className="mt-4 border-t pt-3">
                                <h4 className="text-md font-semibold text-gray-800 mb-2">Médias Associés :</h4>
                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                                    {chambre.medias.map(media => (
                                        <div key={media.id} className="relative">
                                            {media.type.startsWith('photo') ? (
                                                <img src={media.url} alt={`Media ${media.id}`} className="w-full h-auto rounded-md" />
                                            ) : (
                                                <video controls className="w-full h-auto rounded-md">
                                                    <source src={media.url} type={media.type} />
                                                    Votre navigateur ne supporte pas la vidéo.
                                                </video>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                </ScrollArea>
            </DialogContent>
        </Dialog>
    );
};

export default RoomDetailsDialog;