import React from 'react';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
    DialogTrigger
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import {EyeIcon} from "lucide-react";

// Interface pour les détails de maison (doit correspondre à votre modèle API)
interface MaisonDetails {
    id: number;
    adresse: string;
    ville: string;
    description: string | null;
    nombre_chambres: number; // Exemple : si votre API renvoie le nombre de chambres
    chambres: Array<{ // Exemple : si vous voulez lister les chambres associées
        id: number;
        titre: string;
        prix: number;
        disponible: boolean;
    }>;
    // Ajoutez d'autres champs pertinents pour l'affichage des détails
}

interface HouseDetailsDialogProps {
    maison: MaisonDetails; // La maison dont on veut afficher les détails
}

const HouseDetailsDialog: React.FC<HouseDetailsDialogProps> = ({ maison }) => {
    return (
        <Dialog>
            <DialogTrigger asChild>
                <Button variant={"secondary"} size={"sm"}><EyeIcon/></Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[425px] md:max-w-[600px]">
                <DialogHeader>
                    <DialogTitle>Détails de la Maison: {maison.adresse}</DialogTitle>
                    <DialogDescription>
                        Informations complètes sur la maison.
                    </DialogDescription>
                </DialogHeader>
                <ScrollArea className="max-h-[70vh] py-4">
                    <div className="grid gap-4 py-2">
                        <div className="grid grid-cols-3 items-center gap-4">
                            <span className="text-sm font-medium text-gray-700">Adresse:</span>
                            <span className="col-span-2 text-sm">{maison.adresse}</span>
                        </div>
                        <div className="grid grid-cols-3 items-center gap-4">
                            <span className="text-sm font-medium text-gray-700">Ville:</span>
                            <span className="col-span-2 text-sm">{maison.ville}</span>
                        </div>
                        <div className="grid grid-cols-3 items-center gap-4">
                            <span className="text-sm font-medium text-gray-700">Description:</span>
                            <span className="col-span-2 text-sm">{maison.description || 'Non spécifiée'}</span>
                        </div>
                        {maison.nombre_chambres !== undefined && (
                            <div className="grid grid-cols-3 items-center gap-4">
                                <span className="text-sm font-medium text-gray-700">Nombre de chambres:</span>
                                <span className="col-span-2 text-sm">{maison.nombre_chambres}</span>
                            </div>
                        )}

                        {maison.chambres && maison.chambres.length > 0 && (
                            <div className="mt-4 border-t pt-3">
                                <h4 className="text-md font-semibold text-gray-800 mb-2">Chambres associées :</h4>
                                {maison.chambres.map(chambre => (
                                    <div key={chambre.id} className="text-sm text-gray-700 mb-1 pl-2 border-l-2 border-gray-200">
                                        <p>Titre: <span className="font-medium">{chambre.titre}</span></p>
                                        <p>Prix: <span className="font-medium">{chambre.prix.toLocaleString('fr-SN', { style: 'currency', currency: 'XOF' })}</span></p>
                                        <p>Disponible: <span className="font-medium">{chambre.disponible ? 'Oui' : 'Non'}</span></p>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </ScrollArea>
            </DialogContent>
        </Dialog>
    );
};

export default HouseDetailsDialog;