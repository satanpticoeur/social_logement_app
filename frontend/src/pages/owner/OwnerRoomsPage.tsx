import React, {useEffect, useState} from 'react';
import {useNavigate} from 'react-router-dom';
import {authenticatedFetch} from '@/lib/api.ts';
import {toast} from 'sonner';
import RoomDialog from "@/components/room/RoomDialog.tsx";
import {Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle} from "@/components/ui/card.tsx";
import {Button} from "@/components/ui/button.tsx";
import {Popover, PopoverContent, PopoverTrigger} from "@/components/ui/popover.tsx";
import {EllipsisIcon, SquarePenIcon, TrashIcon} from "lucide-react";
import RoomDetailsDialog from "@/components/room/RoomDetailsDialog.tsx";
import {
    Dialog,
    DialogClose,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
    DialogTrigger
} from "@/components/ui/dialog.tsx";
import {useAuth} from "@/context/AuthContext.tsx";

interface Chambre {
    id: number;
    maison_id: number;
    adresse_maison: string;
    titre: string;
    description: string;
    taille: string;
    type: string;
    meublee: boolean;
    salle_de_bain: boolean;
    prix: number; // Un seul champ de prix
    disponible: boolean;
    contrats_actifs: any[];
    media?: Array<{
        id: number;
        url: string;
        type: string; // Ex: 'image', 'video', etc.
        description: string;
    }>;
}

const OwnerRoomsPage: React.FC = () => {
    const {user, isAuthenticated} = useAuth();
    const navigate = useNavigate();
    const [chambres, setChambres] = useState<Chambre[]>([]);
    const [loading, setLoading] = useState<boolean>(true);

    useEffect(() => {
        if (!isAuthenticated || user?.role !== 'proprietaire') {
            toast.error("Accès refusé. Veuillez vous connecter en tant que propriétaire.");
            navigate('/login');
            return;
        }
        fetchChambres();
    }, [isAuthenticated, user, navigate]);

    const fetchChambres = async () => {
        try {
            setLoading(true);
            const data = await authenticatedFetch('proprietaire/chambres', {method: 'GET'});
            console.log('Chambres récupérées=>', data);
            setChambres(data);
            toast.success("Liste des chambres chargée.");
        } catch (error: any) {
            console.error('Erreur lors du chargement des chambres:', error);
            toast.error("Échec du chargement des chambres.", {description: error.message || "Erreur inconnue."});
        } finally {
            setLoading(false);
        }
    };

    const handleDeleteClick = async (chambreId: number) => {
        try {
            await authenticatedFetch(`chambres/${chambreId}`, {
                method: 'DELETE',
            });
            toast.success("Chambre supprimée avec succès !");
            fetchChambres(); // Recharger la liste des chambres après suppression
        } catch (error: any) {
            console.error('Erreur lors de la suppression de la chambre:', error);
            toast.error("Échec de la suppression de la chambre.", {description: error.message || "Erreur inconnue."});
        }
    };

    if (loading) {
        return <div className="text-center">Chargement des chambres...</div>;
    }

    return (
        <div className="container mx-auto p-4">
            <div className={"flex justify-between items-center mb-4"}>
                <h1 className="text-2xl font-bold">Mes Chambres en Location</h1>
                <RoomDialog
                    onRoomActionSuccess={fetchChambres}
                    actionType={'add'} children={
                    <Button>Ajouter une Chambre</Button>
                }/>
            </div>
            {chambres.length === 0 ? (
                <p>Aucune chambre trouvée pour le moment.</p>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {chambres.map(chambre => (
                        <Card key={chambre.id} className="">
                            <CardHeader className="">
                                <div className="flex items-center gap-3">
                                    <div
                                        className="w-12 h-12 p-4 text-primary rounded-full flex items-center justify-center font-bold border shadow-inner">
                                        {chambre.titre.charAt(0).toUpperCase()}
                                    </div>
                                    <div>
                                        <CardTitle className="font-semibold">{chambre.titre}</CardTitle>
                                        <CardDescription className="text-sm">{chambre.adresse_maison}</CardDescription>
                                    </div>
                                </div>
                            </CardHeader>
                            <CardContent className="">
                                <p className="text-foreground text-xl"><span
                                    className="text-muted-foreground text-xs">Taille :</span> {chambre.taille} m²
                                </p>
                                <p className="text-foreground text-xl"><span
                                    className="text-muted-foreground text-xs">Prix :</span> <span
                                    className="text-lg font-bold">{chambre.prix} fcfa</span></p>
                                <p className="text-foreground">
                                    <span className="text-muted-foreground text-xs">Disponible :</span>
                                    <span
                                        className={`ml-2 px-2 py-0.5 rounded-full text-xs font-semibold ${chambre.disponible ? 'bg-green-100 text-chart-2' : 'bg-red-100 text-destructive'}`}>
                                        {chambre.disponible ? 'Oui' : 'Non'}
                                    </span>
                                </p>
                                {chambre.contrats_actifs.length > 0 ? (
                                    <div className="mt-4 border-t pt-3">
                                        <p className="font-semibold text-gray-700">Contrats Actifs :</p>
                                        {chambre.contrats_actifs.map(contrat => (
                                            <div key={contrat.contrat_id} className="text-xs text-gray-600">
                                                Locataire: {contrat.locataire_nom_utilisateur},
                                                Du: {contrat.date_debut} Au: {contrat.date_fin} ({contrat.statut})
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <p className="text-sm text-muted mt-2">Aucun contrat actif pour cette
                                        chambre.</p>
                                )}
                            </CardContent>
                            <CardFooter className="flex justify-end">
                                <Popover>
                                    <PopoverTrigger asChild>
                                        <div
                                            className={"bg-primary rounded-full p-1 cursor-pointer hover:bg-primary-hover"}>
                                            <EllipsisIcon size={16} color={"white"} className={"hover:text-primary"}/>
                                        </div>
                                    </PopoverTrigger>
                                    <PopoverContent className="w-17 space-y-2" align={"center"} side={"top"}>
                                        <RoomDialog
                                            onRoomActionSuccess={fetchChambres}
                                            actionType={'edit'}
                                            chambreToEdit={chambre}
                                            children={<Button variant={"secondary"}
                                                              size={"sm"}><SquarePenIcon/></Button>}
                                        />
                                        <RoomDetailsDialog chambre={chambre}/>
                                        <Dialog>
                                            <DialogTrigger asChild>
                                                <Button
                                                    variant="secondary"
                                                    size="sm"
                                                >
                                                    <TrashIcon size={16}
                                                               className={"hover:text-primary"}/>
                                                </Button>
                                            </DialogTrigger>
                                            <DialogContent>
                                                <DialogHeader>
                                                    <DialogTitle>Confirmer la Suppression</DialogTitle>
                                                    <DialogDescription>
                                                        Êtes-vous sûr de vouloir supprimer cette chambre ? Cette action
                                                        est irréversible et pourrait affecter les contrats liés.
                                                    </DialogDescription>
                                                </DialogHeader>
                                                <div className="flex justify-end space-x-2">
                                                    <DialogClose>Annuler</DialogClose>
                                                    <Button
                                                        variant="destructive"
                                                        onClick={() => handleDeleteClick(chambre.id)}
                                                    >
                                                        Supprimer
                                                    </Button>
                                                </div>
                                            </DialogContent>
                                        </Dialog>
                                    </PopoverContent>
                                </Popover>
                            </CardFooter>
                        </Card>
                    ))}
                </div>
            )}
        </div>
    );
};

export default OwnerRoomsPage;