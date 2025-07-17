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
} from "@/components/ui/dialog.tsx";
import {Calendar} from "@/components/ui/calendar.tsx";
import {Popover, PopoverContent, PopoverTrigger} from "@/components/ui/popover.tsx";
import {format} from "date-fns";
import {ArrowLeftIcon, CalendarIcon} from "lucide-react";
import {Label} from '@/components/ui/label.tsx';
import {Input} from '@/components/ui/input.tsx';
import {useAuth} from "@/context/AuthContext.tsx";

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
    prix: number; // Prix mensuel de la chambre
    disponible: boolean;
    cree_le: string;
    medias: Media[];
}

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:3000';

const SearchRoomDetailsPage: React.FC = () => {
    const {isAuthenticated} = useAuth();
    const {roomId} = useParams<{ roomId: string }>();
    const navigate = useNavigate();
    const [chambre, setChambre] = useState<ChambreDetails | null>(null);
    const [loading, setLoading] = useState(true);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [showRentalDialog, setShowRentalDialog] = useState(false);
    const [dateDebutContrat, setDateDebutContrat] = useState<Date | undefined>(new Date());
    const [dureeMois, setDureeMois] = useState<string>('12');
    const prixMensuel = chambre?.prix || 0;
    const moisCautionFixe = 1;
    const montantCautionEstime = prixMensuel * moisCautionFixe;

    useEffect(() => {
        if (!roomId) {
            toast.error("ID de chambre manquant dans l'URL.");
            navigate(-1);
            return;
        }
        console.log(`Chargement des détails de la chambre avec ID: ${roomId}`);
        fetchChambreDetails();
    }, [roomId, navigate]);

    const fetchChambreDetails = async () => {
        setLoading(true);
        try {
            const response = await fetch(`${BACKEND_URL}/api/locataire/chambres/${roomId}`);
            if (!response.ok) {
                throw new Error(`Erreur ${response.status}: ${response.statusText}`);
            }
            const data: ChambreDetails = await response.json();
            setChambre(data);
            toast.success("Détails de la chambre chargés.");
        } catch (error: any) {
            console.error('Erreur lors du chargement des détails de la chambre:', error);
            toast.error("Échec du chargement des détails.", {description: error.message || "Erreur inconnue."});
            navigate(-1);
        } finally {
            setLoading(false);
        }
    };

    const handleSoumettreDemandeLocation = async () => {
        if (!chambre || !dateDebutContrat || isNaN(Number(dureeMois))) {
            toast.error("Veuillez fournir une date de début et une durée valides.");
            return;
        }
        if (!chambre.disponible) {
            toast.error("Cette chambre n'est plus disponible pour une nouvelle demande de location.");
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
            console.log("Réponse de la demande de location:", response);
            toast.success("Demande de location soumise avec succès !", {
                description: `Le propriétaire doit approuver votre demande avant que le contrat ne soit actif. Caution estimée: ${montantCautionEstime.toLocaleString()} FCFA.`
            });
            setShowRentalDialog(false);
        } catch (error: any) {
            console.error('Erreur lors de la soumission de la demande de location:', error);
            toast.error("Échec de la soumission de la demande.", {description: error.message || "Erreur inconnue."});
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
            <Button variant={"secondary"} size="sm" onClick={() => navigate(-1)} className="mb-6">
                <ArrowLeftIcon/>retour
            </Button>

            <h1 className="text-4xl font-bold mb-4 text-center">{chambre.titre}</h1>
            <p className="text-xl mb-6 text-center">{chambre.adresse_maison}, {chambre.ville_maison}</p>

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
                    <p className="leading-relaxed">
                        {chambre.description || "Aucune description fournie pour cette chambre."}
                    </p>
                </div>

                {chambre.disponible ? (
                    <Dialog open={showRentalDialog} onOpenChange={setShowRentalDialog}>
                        <DialogTrigger asChild onClick={
                            (e) => {
                                e.preventDefault()
                                if(!isAuthenticated) {
                                    navigate('/login');
                                    return;
                                }
                                setShowRentalDialog(true);
                            }
                        }>
                            <Button className="w-full mt-6">
                                Demander en location cette chambre
                            </Button>
                        </DialogTrigger>
                        <DialogContent className="sm:max-w-[425px]">
                            <DialogHeader>
                                <DialogTitle>Soumettre une demande de location</DialogTitle>
                                <DialogDescription>
                                    Veuillez renseigner les détails de votre demande pour la chambre "{chambre.titre}".
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
                                {/* Affichage du montant de la caution calculé, pas de saisie */}
                                <div className="grid grid-cols-4 items-center gap-4">
                                    <Label className="text-right">
                                        Caution Estimée
                                    </Label>
                                    <span className="col-span-3 font-semibold">
                                        {montantCautionEstime.toLocaleString()} FCFA (pour {moisCautionFixe} mois)
                                    </span>
                                </div>
                            </div>
                            <DialogFooter>
                                <Button
                                    onClick={handleSoumettreDemandeLocation}
                                    disabled={isSubmitting || !dateDebutContrat || !dureeMois || Number(dureeMois) <= 0}
                                >
                                    {isSubmitting ? 'Soumission...' : 'Soumettre la demande'}
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

export default SearchRoomDetailsPage;