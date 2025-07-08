// src/pages/LocataireChambreDetailsPage.tsx
import React, {useEffect, useState} from 'react';
import {useNavigate, useParams} from 'react-router-dom';
import {authenticatedFetch} from '@/lib/api.ts';
import {toast} from 'sonner';
import {Button} from "@/components/ui/button.tsx";
import {Badge} from "@/components/ui/badge.tsx";
import {Carousel, CarouselContent, CarouselItem, CarouselNext, CarouselPrevious} from "@/components/ui/carousel.tsx";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger
} from "@/components/ui/dialog.tsx"; // Importez Dialog components
import {Calendar} from "@/components/ui/calendar.tsx";
import {Popover, PopoverContent, PopoverTrigger} from "@/components/ui/popover.tsx";
import {format} from "date-fns";
import {CalendarIcon} from "lucide-react";
import {Label} from '@/components/ui/label.tsx';
import {Input} from '@/components/ui/input.tsx'; // Pour la durée

// Interfaces (doivent être cohérentes avec le backend)
interface Media {
    id: number;
    url: string;
    type: string | null;
    description: string | null;
}

interface ChambreDetails {
    id: number;
    maison_id: number;
    adresse_maison: string;
    ville_maison: string;
    titre: string;
    description: string | null;
    taille: string | null;
    type: string | null;
    meublee: boolean;
    salle_de_bain: boolean;
    prix: number;
    disponible: boolean; // Va être mis à jour après la location
    cree_le: string;
    medias: Media[];
}

const LodgerRoomDetailsPage: React.FC = () => {
    const {chambreId} = useParams<{ chambreId: string }>();
    const navigate = useNavigate();
    const [chambre, setChambre] = useState<ChambreDetails | null>(null);
    const [loading, setLoading] = useState(true);
    const [isSubmitting, setIsSubmitting] = useState(false); // Pour le bouton de soumission
    const [showRentalDialog, setShowRentalDialog] = useState(false); // État pour la modale de location
    const [dateDebutContrat, setDateDebutContrat] = useState<Date | undefined>(new Date()); // Date par défaut aujourd'hui
    const [dureeMois, setDureeMois] = useState<string>('12'); // Durée par défaut 12 mois

    useEffect(() => {
        if (!chambreId) {
            toast.error("ID de chambre manquant dans l'URL.");
            navigate('/locataire/recherche');
            return;
        }
        fetchChambreDetails();
    }, [chambreId, navigate]);

    const fetchChambreDetails = async () => {
        setLoading(true);
        try {
            const data: ChambreDetails = await authenticatedFetch(`locataire/chambres/${chambreId}`, {method: 'GET'});
            setChambre(data);
            toast.success("Détails de la chambre chargés.");
        } catch (error: any) {
            console.error('Erreur lors du chargement des détails de la chambre:', error);
            toast.error("Échec du chargement des détails.", {description: error.message || "Erreur inconnue."});
            navigate('/locataire/recherche');
        } finally {
            setLoading(false);
        }
    };

    const handleLouerChambre = async () => {
        if (!chambre || !dateDebutContrat || isNaN(Number(dureeMois))) {
            toast.error("Veuillez fournir une date de début et une durée valides.");
            return;
        }
        if (!chambre.disponible) {
            toast.error("Cette chambre n'est plus disponible pour la location.");
            return;
        }

        setIsSubmitting(true);
        try {
            const payload = {
                date_debut: format(dateDebutContrat, 'yyyy-MM-dd'),
                duree_mois: Number(dureeMois)
            };
            const response = await authenticatedFetch(`locataire/chambres/${chambre.id}/louer`, {
                method: 'POST',
                body: JSON.stringify(payload),
            });
            console.log("Réponse de la location de chambre:", response);
            toast.success("Félicitations ! La chambre est louée et votre contrat a été généré.");
            setShowRentalDialog(false); // Fermer la modale
            // Mettre à jour l'état de la chambre pour qu'elle apparaisse indisponible
            setChambre(prevChambre => prevChambre ? {...prevChambre, disponible: false} : null);
            // Optionnel: Rediriger l'utilisateur vers son tableau de bord de contrats
            navigate('/locataire/contrats');

        } catch (error: any) {
            console.error('Erreur lors de la location de la chambre:', error);
            toast.error("Échec de la location de la chambre.", {description: error.message || "Erreur inconnue."});
        } finally {
            setIsSubmitting(false);
        }
    };

    if (loading) {
        return <div className="text-center p-8">Chargement des détails de la chambre...</div>;
    }

    if (!chambre) {
        return <div className="text-center p-8 text-red-600">Chambre non trouvée ou non disponible.</div>;
    }

    return (
        <div className="container mx-auto p-4">
            <Button onClick={() => navigate(-1)} className="mb-6">Retour à la recherche</Button>

            <h1 className="text-4xl font-bold mb-4 text-center">{chambre.titre}</h1>
            <p className="text-xl text-gray-700 mb-6 text-center">{chambre.adresse_maison}, {chambre.ville_maison}</p>

            {chambre.medias && chambre.medias.length > 0 ? (
                <Carousel className="w-full max-w-2xl mx-auto mb-8 border rounded-lg overflow-hidden shadow-md">
                    <CarouselContent>
                        {chambre.medias.map((media, index) => (
                            <CarouselItem key={media.id || index}>
                                <div className="p-1">
                                    <img
                                        src={media.url}
                                        alt={media.description || `Photo de ${chambre.titre} ${index + 1}`}
                                        className="w-full h-96 object-cover rounded-md"
                                    />
                                </div>
                            </CarouselItem>
                        ))}
                    </CarouselContent>
                    <CarouselPrevious/>
                    <CarouselNext/>
                </Carousel>
            ) : (
                <div
                    className="w-full max-w-2xl mx-auto h-96  flex items-center justify-center rounded-lg mb-8 text-gray-500">
                    Aucune photo disponible pour cette chambre.
                </div>
            )}

            <div className="p-8 rounded-lg shadow-lg max-w-3xl mx-auto">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                    <div>
                        <h2 className="text-2xl font-semibold mb-3">Informations Clés</h2>
                        <p className="text-lg mb-2"><strong>Prix:</strong> {chambre.prix.toLocaleString()} FCFA/mois</p>
                        <p className="text-lg mb-2"><strong>Taille:</strong> {chambre.taille || 'Non spécifiée'}</p>
                        <p className="text-lg mb-2"><strong>Type:</strong> {chambre.type || 'Non spécifié'}</p>
                        <p className="text-lg mb-2">
                            <strong>Statut:</strong>
                            <Badge variant={chambre.disponible ? "default" : "destructive"} className="ml-2">
                                {chambre.disponible ? 'Disponible' : 'Indisponible'}
                            </Badge>
                        </p>
                    </div>
                    <div>
                        <h2 className="text-2xl font-semibold mb-3">Équipements</h2>
                        <p className="text-lg mb-2">
                            <strong>Meublée:</strong>
                            <Badge variant={chambre.meublee ? "default" : "outline"} className="ml-2">
                                {chambre.meublee ? 'Oui' : 'Non'}
                            </Badge>
                        </p>
                        <p className="text-lg mb-2">
                            <strong>Salle de Bain Privée:</strong>
                            <Badge variant={chambre.salle_de_bain ? "default" : "outline"} className="ml-2">
                                {chambre.salle_de_bain ? 'Oui' : 'Non'}
                            </Badge>
                        </p>
                    </div>
                </div>

                <div className="mb-6">
                    <h2 className="text-2xl font-semibold mb-3">Description</h2>
                    <p className="text-gray-800 leading-relaxed">
                        {chambre.description || "Aucune description fournie pour cette chambre."}
                    </p>
                </div>

                {chambre.disponible ? (
                    <Dialog open={showRentalDialog} onOpenChange={setShowRentalDialog}>
                        <DialogTrigger asChild>
                            <Button className="w-full text-lg py-3 mt-6">
                                Louer cette chambre
                            </Button>
                        </DialogTrigger>
                        <DialogContent className="sm:max-w-[425px]">
                            <DialogHeader>
                                <DialogTitle>Confirmer la location</DialogTitle>
                                <DialogDescription>
                                    Veuillez confirmer les détails de la location pour la chambre "{chambre.titre}".
                                </DialogDescription>
                            </DialogHeader>
                            <div className="grid gap-4 py-4">
                                <div className="grid grid-cols-4 items-center gap-4">
                                    <Label htmlFor="dateDebutContrat" className="text-right">
                                        Date de début
                                    </Label>
                                    <Popover>
                                        <PopoverTrigger asChild>
                                            <Button
                                                variant={"outline"}
                                                className={`col-span-3 justify-start text-left font-normal ${!dateDebutContrat && "text-muted-foreground"}`}
                                            >
                                                <CalendarIcon className="mr-2 h-4 w-4"/>
                                                {dateDebutContrat ? format(dateDebutContrat, "PPP") :
                                                    <span>Choisir une date</span>}
                                            </Button>
                                        </PopoverTrigger>
                                        <PopoverContent className="w-auto p-0">
                                            <Calendar
                                                mode="single"
                                                selected={dateDebutContrat}
                                                onSelect={setDateDebutContrat}
                                                autoFocus={
                                                    true
                                                }
                                            />
                                        </PopoverContent>
                                    </Popover>
                                </div>
                                <div className="grid grid-cols-4 items-center gap-4">
                                    <Label htmlFor="dureeMois" className="text-right">
                                        Durée (mois)
                                    </Label>
                                    <Input
                                        id="dureeMois"
                                        type="number"
                                        value={dureeMois}
                                        onChange={(e) => setDureeMois(e.target.value)}
                                        className="col-span-3"
                                        min="1"
                                    />
                                </div>
                                {/* Vous pouvez ajouter ici des champs pour le montant de la caution, etc. si nécessaire pour le MVP */}
                            </div>
                            <DialogFooter>
                                <Button
                                    onClick={handleLouerChambre}
                                    disabled={isSubmitting || !dateDebutContrat || !dureeMois || Number(dureeMois) <= 0}
                                >
                                    {isSubmitting ? 'Finalisation...' : 'Confirmer la location'}
                                </Button>
                            </DialogFooter>
                        </DialogContent>
                    </Dialog>
                ) : (
                    <Button className="w-full text-lg py-3 mt-6" disabled>
                        Chambre Indisponible
                    </Button>
                )}
            </div>
        </div>
    );
};

export default LodgerRoomDetailsPage;