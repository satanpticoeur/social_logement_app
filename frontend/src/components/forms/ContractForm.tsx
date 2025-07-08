// frontend/src/components/forms/ContractForm.tsx

import React, {useEffect, useState} from 'react';
import {useNavigate} from 'react-router-dom';
import type {Chambre, Contrat, Utilisateur} from '@/types/common.ts';
import {Button} from '@/components/ui/button';
import {Input} from '@/components/ui/input';
import {Label} from '@/components/ui/label';
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from '@/components/ui/select';
import {Textarea} from '@/components/ui/textarea';
import {toast} from "sonner";
import {Calendar} from '@/components/ui/calendar'; // Pour le sélecteur de date
import {Popover, PopoverContent, PopoverTrigger} from '@/components/ui/popover'; // Pour le sélecteur de date
import {format} from 'date-fns';
import {cn} from '@/lib/utils';
import {CalendarIcon} from "lucide-react"; // Pour la fusion des classes Tailwind

interface ContractFormProps {
    contratToEdit?: Contrat; // Optionnel, si on est en mode modification
}

const ContractForm: React.FC<ContractFormProps> = ({contratToEdit}) => {
    const navigate = useNavigate();
    const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

    const [locataires, setLocataires] = useState<Utilisateur[]>([]);
    const [chambres, setChambres] = useState<Chambre[]>([]);
    const [loadingData, setLoadingData] = useState(true);
    const [formError, setFormError] = useState<string | null>(null);

    // État du formulaire
    const [formData, setFormData] = useState({
        locataire_id: '',
        chambre_id: '',
        date_debut: '',
        date_fin: '',
        montant_caution: '',
        mois_caution: '',
        description: '',
        mode_paiement: '',
        periodicite: '',
        statut: 'actif', // Valeur par défaut
    });

    // Gérer les dates comme des objets Date pour le calendrier
    const [startDate, setStartDate] = useState<Date | undefined>(undefined);
    const [endDate, setEndDate] = useState<Date | undefined>(undefined);

    useEffect(() => {
        // Charger les locataires et les chambres pour les sélecteurs
        const fetchData = async () => {
            try {
                const [usersRes, roomsRes] = await Promise.all([
                    fetch(`${BACKEND_URL}/api/utilisateurs`),
                    fetch(`${BACKEND_URL}/api/chambres`)
                ]);

                if (!usersRes.ok || !roomsRes.ok) {
                    throw new Error('Failed to fetch users or rooms');
                }

                const usersData: Utilisateur[] = await usersRes.json();
                const roomsData: Chambre[] = await roomsRes.json();

                setLocataires(usersData.filter(user => user.role === 'locataire')); // Filtrer par rôle 'locataire'
                setChambres(roomsData);
            } catch (error) {
                console.error('Error fetching initial data:', error);
                setFormError('Erreur lors du chargement des données (locataires/chambres).');
            } finally {
                setLoadingData(false);
            }
        };

        fetchData();

        // Si en mode édition, pré-remplir le formulaire
        if (contratToEdit) {
            console.log("Contrat à éditer:", contratToEdit);
            setFormData({
                locataire_id: contratToEdit.locataire_id.toString(),
                chambre_id: contratToEdit.chambre_id.toString(),
                date_debut: contratToEdit.date_debut,
                date_fin: contratToEdit.date_fin,
                montant_caution: contratToEdit.montant_caution.toString(),
                mois_caution: contratToEdit.mois_caution.toString(),
                description: contratToEdit.description || '',
                mode_paiement: contratToEdit.mode_paiement || '',
                periodicite: contratToEdit.periodicite || '',
                statut: contratToEdit.statut || 'actif',
            });
            setStartDate(new Date(contratToEdit.date_debut));
            setEndDate(new Date(contratToEdit.date_fin));
        }
    }, [contratToEdit, BACKEND_URL]);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        const {id, value} = e.target;
        setFormData(prev => ({...prev, [id]: value}));
    };

    const handleSelectChange = (id: string, value: string) => {
        setFormData(prev => ({...prev, [id]: value}));
    };

    const handleDateChange = (date: Date | undefined, field: 'date_debut' | 'date_fin') => {
        if (field === 'date_debut') {
            setStartDate(date);
            setFormData(prev => ({...prev, date_debut: date ? format(date, 'yyyy-MM-dd') : ''}));
        } else {
            setEndDate(date);
            setFormData(prev => ({...prev, date_fin: date ? format(date, 'yyyy-MM-dd') : ''}));
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setFormError(null);

        // Validation de base
        if (!formData.locataire_id || !formData.chambre_id || !formData.date_debut || !formData.date_fin || !formData.montant_caution || !formData.periodicite || !formData.mode_paiement) {
            setFormError("Veuillez remplir tous les champs obligatoires (Locataire, Chambre, Dates, Caution, Périodicité, Mode de paiement).");
            return;
        }
        if (new Date(formData.date_debut) >= new Date(formData.date_fin)) {
            setFormError("La date de début doit être antérieure à la date de fin.");
            return;
        }

        const payload = {
            ...formData,
            locataire_id: parseInt(formData.locataire_id),
            chambre_id: parseInt(formData.chambre_id),
            montant_caution: parseFloat(formData.montant_caution),
            mois_caution: parseInt(formData.mois_caution),
        };

        const method = contratToEdit ? 'PUT' : 'POST';
        const url = contratToEdit ? `${BACKEND_URL}/api/contrats/${contratToEdit.id}` : `${BACKEND_URL}/api/contrats`;

        try {
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
            });

            const data = await response.json();

            if (!response.ok) {
                // Gérer les erreurs de l'API Flask (400, 404, 500)
                const errorMessage = data.description || data.message || "Une erreur est survenue lors de l'opération.";
                throw new Error(errorMessage);
            }

            toast.success(contratToEdit ? "Contrat mis à jour" : "Contrat créé", {
                description: `Le contrat a été ${contratToEdit ? 'mis à jour' : 'créé'} avec succès.`,
            });

            navigate('/contracts'); // Rediriger vers la liste des contrats après succès

        } catch (error: unknown) {
            console.error("Erreur soumission contrat:", error);
            const errorMessage = error instanceof Error ? error.message : "Erreur inattendue lors de la soumission.";
            setFormError(errorMessage);
            toast.error("Erreur", {
                description: errorMessage || "Échec de l'opération sur le contrat.",
            });
        }
    };

    if (loadingData) {
        return <div className="text-center mt-10 text-muted-foreground">Chargement des données du formulaire...</div>;
    }

    return (
        <div className="p-4 bg-background text-foreground max-w-2xl mx-auto">
            <h1 className="text-3xl font-bold mb-6 text-center text-primary">
                {contratToEdit ? "Modifier le Contrat" : "Créer un Nouveau Contrat"}
            </h1>

            <form onSubmit={handleSubmit} className="grid gap-6 bg-card p-6 rounded-lg shadow-md border border-border">
                {formError && (
                    <div
                        className="bg-destructive/10 text-destructive border border-destructive p-3 rounded-md text-sm">
                        {formError}
                    </div>
                )}

                {/* Locataire */}
                <div>
                    <Label htmlFor="locataire_id" className="mb-2 block">Locataire <span
                        className="text-red-500">*</span></Label>
                    <Select
                        value={formData.locataire_id}
                        onValueChange={(value) => handleSelectChange('locataire_id', value)}
                        disabled={!!contratToEdit} // Ne pas permettre de changer le locataire pour un contrat existant (logique métier)
                    >
                        <SelectTrigger id="locataire_id">
                            <SelectValue placeholder="Sélectionner un locataire"/>
                        </SelectTrigger>
                        <SelectContent>
                            {locataires.length === 0 &&
                                <SelectItem value="" disabled>Aucun locataire disponible</SelectItem>}
                            {locataires.map(locataire => (
                                <SelectItem key={locataire.id} value={locataire.id.toString()}>
                                    {locataire.nom_utilisateur} ({locataire.email})
                                </SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                </div>

                {/* Chambre */}
                <div>
                    <Label htmlFor="chambre_id" className="mb-2 block">Chambre <span
                        className="text-red-500">*</span></Label>
                    <Select
                        value={formData.chambre_id}
                        onValueChange={(value) => handleSelectChange('chambre_id', value)}
                        disabled={!!contratToEdit} // Ne pas permettre de changer la chambre pour un contrat existant (logique métier)
                    >
                        <SelectTrigger id="chambre_id">
                            <SelectValue placeholder="Sélectionner une chambre"/>
                        </SelectTrigger>
                        <SelectContent>
                            {chambres.length === 0 &&
                                <SelectItem value="" disabled>Aucune chambre disponible</SelectItem>}
                            {chambres.map(chambre => (
                                <SelectItem key={chambre.id} value={chambre.id.toString()}>
                                    {chambre.titre} ({chambre.prix?.toLocaleString()} XOF)
                                </SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                </div>

                {/* Date Début */}
                <div>
                    <Label htmlFor="date_debut" className="mb-2 block">Date de Début <span
                        className="text-red-500">*</span></Label>
                    <Popover>
                        <PopoverTrigger asChild>
                            <Button
                                variant={"outline"}
                                className={cn(
                                    "w-full bg-transparent justify-start text-left font-normal",
                                    !startDate && "text-muted-foreground"
                                )}
                            >
                                <CalendarIcon className="mr-2 h-4 w-4"/>
                                {startDate ? format(startDate, "PPP") : <span>Choisir une date</span>}
                            </Button>
                        </PopoverTrigger>
                        <PopoverContent className="w-auto p-0" align="start">
                            <Calendar
                                mode="single"
                                selected={startDate}
                                onSelect={(date) => handleDateChange(date, 'date_debut')}
                                autoFocus={!startDate}
                            />
                        </PopoverContent>
                    </Popover>
                </div>

                {/* Date Fin */}
                <div>
                    <Label htmlFor="date_fin" className="mb-2 block">Date de Fin <span className="text-red-500">*</span></Label>
                    <Popover>
                        <PopoverTrigger asChild>
                            <Button
                                variant={"outline"}
                                className={cn(
                                    "w-full bg-transparent justify-start text-left font-normal",
                                    !endDate && "text-muted-foreground"
                                )}
                            >
                                <CalendarIcon className="mr-2 h-4 w-4"/>
                                {endDate ? format(endDate, "PPP") : <span>Choisir une date</span>}
                            </Button>
                        </PopoverTrigger>
                        <PopoverContent className="w-auto p-0" align="start">
                            <Calendar
                                mode="single"
                                selected={endDate}
                                onSelect={(date) => handleDateChange(date, 'date_fin')}
                                autoFocus={!endDate}
                            />
                        </PopoverContent>
                    </Popover>
                </div>

                {/* Montant Caution */}
                <div>
                    <Label htmlFor="montant_caution" className="mb-2 block">Montant Caution <span
                        className="text-red-500">*</span></Label>
                    <Input
                        type="number"
                        id="montant_caution"
                        value={formData.montant_caution}
                        onChange={handleChange}
                        placeholder="Ex: 150000"
                        step="1000"
                        min="0"
                    />
                </div>

                {/* Mois Caution */}
                <div>
                    <Label htmlFor="mois_caution" className="mb-2 block">Mois de Caution</Label>
                    <Input
                        type="number"
                        id="mois_caution"
                        value={formData.mois_caution}
                        onChange={handleChange}
                        placeholder="Ex: 3"
                        min="0"
                    />
                </div>

                {/* Mode de Paiement */}
                <div>
                    <Label htmlFor="mode_paiement" className="mb-2 block">Mode de Paiement <span
                        className="text-red-500">*</span></Label>
                    <Select
                        value={formData.mode_paiement}
                        onValueChange={(value) => handleSelectChange('mode_paiement', value)}
                    >
                        <SelectTrigger id="mode_paiement">
                            <SelectValue placeholder="Sélectionner un mode de paiement"/>
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="virement bancaire">Virement Bancaire</SelectItem>
                            <SelectItem value="cash">Cash</SelectItem>
                            <SelectItem value="mobile money">Mobile Money</SelectItem>
                        </SelectContent>
                    </Select>
                </div>

                {/* Périodicité */}
                <div>
                    <Label htmlFor="periodicite" className="mb-2 block">Périodicité <span
                        className="text-red-500">*</span></Label>
                    <Select
                        value={formData.periodicite}
                        onValueChange={(value) => handleSelectChange('periodicite', value)}
                    >
                        <SelectTrigger id="periodicite">
                            <SelectValue placeholder="Sélectionner la périodicité"/>
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="journalier">Journalier</SelectItem>
                            <SelectItem value="hebdomadaire">Hebdomadaire</SelectItem>
                            <SelectItem value="mensuel">Mensuel</SelectItem>
                        </SelectContent>
                    </Select>
                </div>

                {/* Statut (uniquement en mode modification) */}
                {contratToEdit && (
                    <div>
                        <Label htmlFor="statut" className="mb-2 block">Statut du Contrat</Label>
                        <Select
                            value={formData.statut}
                            onValueChange={(value) => handleSelectChange('statut', value)}
                        >
                            <SelectTrigger id="statut">
                                <SelectValue placeholder="Sélectionner le statut"/>
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="actif">Actif</SelectItem>
                                <SelectItem value="resilié">Résilié</SelectItem>
                            </SelectContent>
                        </Select>
                    </div>
                )}

                {/* Description */}
                <div>
                    <Label htmlFor="description" className="mb-2 block">Description (optionnel)</Label>
                    <Textarea
                        id="description"
                        value={formData.description}
                        onChange={handleChange}
                        placeholder="Ajouter une description pour le contrat..."
                        rows={4}
                    />
                </div>

                <Button type="submit" className="w-full">
                    {contratToEdit ? "Mettre à jour le Contrat" : "Créer le Contrat"}
                </Button>
            </form>
        </div>
    );
};

export default ContractForm;