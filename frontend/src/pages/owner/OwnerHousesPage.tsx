import React, {useEffect, useState} from 'react';
import {useNavigate} from 'react-router-dom';
import {authenticatedFetch} from '@/lib/api.ts';
import {toast} from 'sonner';
import {HouseDialogForm} from '@/components/house/HouseDialogForm.tsx';
import {Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle} from "@/components/ui/card.tsx";
import {Button} from "@/components/ui/button.tsx";
import {Popover, PopoverContent, PopoverTrigger} from "@/components/ui/popover.tsx";
import {EllipsisIcon, SquarePenIcon, TrashIcon} from "lucide-react";
import {
    Dialog,
    DialogClose,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
    DialogTrigger
} from "@/components/ui/dialog.tsx";
import HouseDetailsDialog from "@/components/house/HouseDetailsDialog.tsx";
import {useAuth} from "@/context/AuthContext.tsx";


interface Maison {
    id: number;
    adresse: string;
    ville: string;
    description: string;
    nombre_chambres: number;
    chambres: Array<{ // Exemple : si vous voulez lister les chambres associées
        id: number;
        titre: string;
        prix: number;
        disponible: boolean;
    }>;
    cree_le: string; // Date au format ISO string
}

const OwnerHousesPage: React.FC = () => {
    const {user, isAuthenticated} = useAuth();
    const navigate = useNavigate();
    const [maisons, setMaisons] = useState<Maison[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (!isAuthenticated || user?.role !== 'proprietaire') {
            toast.error("Accès refusé. Veuillez vous connecter en tant que propriétaire.");
            navigate('/login');
            return;
        }
        fetchMaisons();
    }, [isAuthenticated, user, navigate]);

    const fetchMaisons = async () => {
        try {
            setLoading(true);
            const data: Maison[] = await authenticatedFetch('proprietaire/maisons', {method: 'GET'});
            setMaisons(data);
            console.log('Maisons récupérées:', data);
            toast.success("Liste des maisons chargée.");
        } catch (error: any) {
            console.error('Erreur lors du chargement des maisons:', error);
            toast.error("Échec du chargement des maisons.", {description: error.message || "Erreur inconnue."});
        } finally {
            setLoading(false);
        }
    };

    const handleDeleteHouse = async (maisonId: number) => {
        try {
            await authenticatedFetch(`maisons/${maisonId}`, {
                method: 'DELETE',
            });
            toast.success("Maison supprimée avec succès !");
            fetchMaisons(); // Recharger la liste
        } catch (error: any) {
            console.error('Erreur lors de la suppression de la maison:', error);
            toast.error("Échec de la suppression de la maison.", {description: error.message || "Erreur inconnue."});
        }
    };

    if (loading) {
        return <p>Chargement des maisons...</p>;
    }

    return (
        <div className="container mx-auto p-4">
            <div className="flex justify-between items-center mb-4">
                <h2 className="text-2xl font-bold">Mes Propriétés</h2>
                <HouseDialogForm onHouseActionSuccess={fetchMaisons} actionType={'add'} children={
                    <Button>
                        Ajouter une maison
                    </Button>
                }/>
            </div>
            {maisons.length === 0 ? (
                <p>Vous n'avez pas encore de maisons enregistrées. Ajoutez-en une pour commencer !</p>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-4">
                    {maisons.map((maison) => (
                        <Card key={maison.id} className="">
                            <CardHeader>
                                <CardTitle className="text-lg font-semibold">
                                    {maison.adresse && maison.ville ? (
                                        <span>{maison.adresse}, {maison.ville}</span>
                                    ) : (
                                        <span>{maison.adresse}{maison.ville}</span>
                                    )}

                                </CardTitle>
                                <CardDescription className="text-sm">
                                    {maison.description || "Aucune description fournie."}
                                </CardDescription>
                            </CardHeader>
                            <CardContent className={""}>
                                <p className="text-sm">Nombre de chambres: {maison.nombre_chambres}</p>
                                <p className="text-sm">Créé le: {new Date(maison.cree_le).toLocaleDateString()}</p>
                            </CardContent>
                            <CardFooter className="flex justify-end">
                                <Popover>
                                    <PopoverTrigger asChild>
                                        <div
                                            className={"bg-primary rounded-full p-1 cursor-pointer hover:bg-primary-hover"}>
                                            <EllipsisIcon size={16} color={"white"} className={"hover:text-primary"}/>
                                        </div>
                                    </PopoverTrigger>
                                    <PopoverContent className="w-18 space-y-2" align={"center"} side={"top"}>
                                        <HouseDialogForm
                                            onHouseActionSuccess={fetchMaisons}
                                            actionType={'edit'}
                                            houseToEdit={maison}
                                            children={<Button variant={"secondary"}
                                                              size={"sm"}><SquarePenIcon/></Button>}
                                        />
                                        <HouseDetailsDialog maison={maison}/>
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
                                                        Êtes-vous sûr de vouloir supprimer cette maison ? Cette action
                                                        est irréversible et pourrait affecter les contrats liés.
                                                    </DialogDescription>
                                                </DialogHeader>
                                                <div className="flex justify-end space-x-2">
                                                    <DialogClose>Annuler</DialogClose>
                                                    <Button
                                                        variant="destructive"
                                                        onClick={() => handleDeleteHouse(maison.id)}
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

export default OwnerHousesPage;