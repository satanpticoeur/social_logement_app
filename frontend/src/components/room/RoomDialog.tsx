import React, {useState, useEffect, type ReactNode} from 'react';
import {authenticatedFetch} from '@/lib/api'; // On va s'assurer que cette fonction gère bien le FormData
import {toast} from 'sonner';

import {
    Dialog, DialogClose,
    DialogContent,
    DialogDescription, DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger
} from "@/components/ui/dialog";
import {Button} from "@/components/ui/button";
import {Label} from "@/components/ui/label";
import {Input} from "@/components/ui/input";
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from "@/components/ui/select";
import {Textarea} from "@/components/ui/textarea";
import {ScrollArea} from "@/components/ui/scroll-area";

// S'assurer que l'interface Media est définie quelque part ou importée
interface Media {
    id: number;
    url: string;
    type: string | null;
    description: string | null;
}

interface Chambre {
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
    medias?: Media[]; // Optionnel, pour les médias associés
}

interface Maison {
    id: number;
    adresse: string;
    ville: string;
}

interface RoomDialogProps {
    onRoomActionSuccess: () => void;
    chambreToEdit?: Chambre | null;
    actionType: 'add' | 'edit';
    children: ReactNode;
}

const RoomDialog: React.FC<RoomDialogProps> = ({onRoomActionSuccess, chambreToEdit, actionType, children}) => {
    const [maisons, setMaisons] = useState<Maison[]>([]);
    const [formData, setFormData] = useState({
        maison_id: '',
        titre: '',
        description: '',
        taille: '',
        type: '',
        meublee: false,
        salle_de_bain: false,
        prix: '',
        disponible: true,
    });
    const [loadingMaisons, setLoadingMaisons] = useState(true);
    const [submitting, setSubmitting] = useState(false);
    const [dialogOpen, setDialogOpen] = useState(false);

    const [selectedFiles, setSelectedFiles] = useState<FileList | null>(null);
    const [existingMedias, setExistingMedias] = useState<Media[]>([]);

    const isEditing = actionType === 'edit';
    const dialogTitle = isEditing ? "Modifier la Chambre" : "Ajouter une Nouvelle Chambre";
    const submitButtonText = isEditing ? (submitting ? 'Mise à jour...' : 'Mettre à jour la chambre') : (submitting ? 'Ajout en cours...' : 'Ajouter la chambre');

    useEffect(() => {
        if (dialogOpen) {
            fetchMaisons();
            if (isEditing && chambreToEdit) {
                setFormData({
                    maison_id: String(chambreToEdit.maison_id),
                    titre: chambreToEdit.titre,
                    description: chambreToEdit.description || '',
                    taille: chambreToEdit.taille || '',
                    type: chambreToEdit.type || '',
                    meublee: chambreToEdit.meublee,
                    salle_de_bain: chambreToEdit.salle_de_bain,
                    prix: String(chambreToEdit.prix),
                    disponible: chambreToEdit.disponible,
                });
                setExistingMedias(chambreToEdit.medias || []);
            } else {
                setFormData({
                    maison_id: '',
                    titre: '',
                    description: '',
                    taille: '',
                    type: '',
                    meublee: false,
                    salle_de_bain: false,
                    prix: '',
                    disponible: true,
                });
                setSelectedFiles(null);
                setExistingMedias([]);
            }
        }
    }, [dialogOpen, isEditing, chambreToEdit]);

    const fetchMaisons = async () => {
        try {
            setLoadingMaisons(true);
            const data: Maison[] = await authenticatedFetch('proprietaire/maisons', {method: 'GET'});
            setMaisons(data);
            if (!isEditing && data.length > 0 && !formData.maison_id) {
                setFormData(prev => ({...prev, maison_id: String(data[0].id)}));
            }
        } catch (error: any) {
            console.error('Erreur lors du chargement des maisons:', error);
            toast.error("Échec du chargement des maisons.", {description: error.message || "Erreur inconnue."});
        } finally {
            setLoadingMaisons(false);
        }
    };

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        const {name, value, type} = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value,
        }));
    };

    const handleSelectChange = (value: string) => {
        setFormData(prev => ({
            ...prev,
            maison_id: value,
        }));
    };

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        // Logique de validation simple : s'assurer qu'il y a des fichiers
        if (e.target.files && e.target.files.length > 0) {
            setSelectedFiles(e.target.files);
            console.log(`${e.target.files.length} fichier(s) sélectionné(s) dans le frontend.`);
        } else {
            setSelectedFiles(null);
            console.log("Aucun fichier sélectionné dans le frontend.");
        }
    };

    const handleRemoveExistingMedia = async (mediaId: number) => {
        if (!window.confirm("Êtes-vous sûr de vouloir supprimer cette photo ?")) return;
        try {
            await authenticatedFetch(`proprietaire/medias/${mediaId}`, {method: 'DELETE'});
            toast.success("Photo supprimée !");
            setExistingMedias(prev => prev.filter(media => media.id !== mediaId));
            onRoomActionSuccess();
        } catch (error: any) {
            toast.error("Échec de la suppression de la photo.", {description: error.message || "Erreur inconnue."});
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setSubmitting(true);
        let chambreId: number | null = null;
        try {
            const dataToSend = {
                ...formData,
                maison_id: parseInt(formData.maison_id),
                prix: parseFloat(formData.prix),
            };

            let response;
            if (isEditing && chambreToEdit) {
                response = await authenticatedFetch(`proprietaire/chambres/${chambreToEdit.id}`, {
                    method: 'PUT',
                    body: JSON.stringify(dataToSend),
                });
                chambreId = chambreToEdit.id;
                toast.success(response.message || "Chambre mise à jour avec succès !");
            } else {
                response = await authenticatedFetch('proprietaire/chambres', {
                    method: 'POST',
                    body: JSON.stringify(dataToSend),
                });
                console.log("response", response);
                // S'assurer que le backend renvoie bien { chambre_id: ID }
                if (response && response.chambre.id) {
                    chambreId = response.chambre.id;
                    toast.success(response.message || "Chambre ajoutée avec succès !");
                } else {
                    throw new Error("L'ID de la chambre n'a pas été renvoyé par le serveur.");
                }
            }


            // --- TÉLÉVERSEMENT DES FICHIERS APRÈS CRÉATION/MISE À JOUR DE LA CHAMBRE ---
            if (chambreId && selectedFiles && selectedFiles.length > 0) {
                console.log(`Tentative de téléversement de ${selectedFiles.length} fichier(s) pour la chambre ID:`, chambreId);
                const uploadFormData = new FormData(); // Utiliser un nom différent pour éviter la confusion
                for (let i = 0; i < selectedFiles.length; i++) {
                    uploadFormData.append('files', selectedFiles[i]);
                }

                await authenticatedFetch(`chambres/${chambreId}/medias`, {
                    method: 'POST',
                    body: uploadFormData,
                });
                toast.success("Photos téléversées avec succès !");
            } else {
                console.log("Aucun nouveau fichier sélectionné pour le téléversement ou chambreId manquant.");
            }

            onRoomActionSuccess();
            setDialogOpen(false);

        } catch (error: any) {
            console.error(`Erreur lors de ${isEditing ? 'la modification' : 'l\'ajout'} de la chambre:`, error);
            toast.error(`Échec de ${isEditing ? 'la modification' : 'l\'ajout'} de la chambre.`, {description: error.message || "Erreur inconnue."});
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogTrigger asChild>
                {children}
            </DialogTrigger>
            <DialogContent className="">
                <DialogHeader>
                    <DialogTitle>{dialogTitle}</DialogTitle>
                    <DialogDescription>
                        {isEditing ? "Modifiez les informations de la chambre." : "Remplissez les informations de la chambre à ajouter."}
                    </DialogDescription>
                </DialogHeader>
                <ScrollArea className="max-h-[70vh] p-4">
                    <div className="mt-9 p-4">
                        {loadingMaisons ? (
                            <p>Chargement des maisons...</p>
                        ) : maisons.length === 0 ? (
                            <div className="p-4 mb-4" role="alert">
                                <p className="font-bold">Attention</p>
                                <p>Vous n'avez pas encore de maison. Veuillez ajouter une maison avant d'ajouter une
                                    chambre.</p>
                            </div>
                        ) : (
                            <form onSubmit={handleSubmit} className="space-y-4">
                                <div>
                                    <Label htmlFor="maison_id" className="text-sm font-medium">Maison associée</Label>
                                    <Select
                                        name="maison_id"
                                        value={formData.maison_id}
                                        onValueChange={handleSelectChange}
                                        disabled={isEditing}
                                    >
                                        <SelectTrigger className="w-full">
                                            <SelectValue placeholder="Sélectionner une maison"/>
                                        </SelectTrigger>
                                        <SelectContent>
                                            {maisons.map((maison) => (
                                                <SelectItem key={maison.id} value={String(maison.id)}>
                                                    {maison.adresse}, {maison.ville}
                                                </SelectItem>
                                            ))}
                                        </SelectContent>
                                    </Select>
                                </div>
                                <div>
                                    <Label htmlFor="titre" className="text-sm font-medium">Titre de la Chambre</Label>
                                    <Input type="text" id="titre" name="titre" value={formData.titre}
                                           onChange={handleInputChange} required className="mt-1 "/>
                                </div>
                                <div>
                                    <Label htmlFor="description" className="text-sm font-medium">Description</Label>
                                    <Textarea id="description" name="description" value={formData.description}
                                              onChange={handleInputChange} rows={3} className="mt-1 "></Textarea>
                                </div>
                                <div>
                                    <Label htmlFor="taille" className="text-sm font-medium">Taille (ex: 12m²)</Label>
                                    <Input type="text" id="taille" name="taille" value={formData.taille}
                                           onChange={handleInputChange} className="mt-1 "/>
                                </div>
                                <div>
                                    <Label htmlFor="type" className="text-sm font-medium">Type (ex: simple,
                                        appartement)</Label>
                                    <Input type="text" id="type" name="type" value={formData.type}
                                           onChange={handleInputChange} className="mt-1 "/>
                                </div>
                                <div className="flex items-center">
                                    <Input type="checkbox" id="meublee" name="meublee" checked={formData.meublee}
                                           onChange={handleInputChange} className="h-4 w-4 rounded"/>
                                    <Label htmlFor="meublee" className="ml-2 text-sm">Meublée</Label>
                                </div>
                                <div className="flex items-center">
                                    <Input type="checkbox" id="salle_de_bain" name="salle_de_bain"
                                           checked={formData.salle_de_bain} onChange={handleInputChange}
                                           className="h-4 w-4 rounded"/>
                                    <Label htmlFor="salle_de_bain" className="ml-2 text-sm">Avec salle de bain
                                        privée</Label>
                                </div>
                                <div>
                                    <Label htmlFor="prix" className="text-sm font-medium">Prix (FCFA)</Label>
                                    <Input type="number" id="prix" name="prix" value={formData.prix}
                                           onChange={handleInputChange} min="0" step="0.01" required className="mt-1 "/>
                                </div>
                                <div className="flex items-center">
                                    <Input type="checkbox" id="disponible" name="disponible"
                                           checked={formData.disponible} onChange={handleInputChange}
                                           className="h-4 w-4 rounded"/>
                                    <Label htmlFor="disponible" className="ml-2 text-sm">Est disponible à la
                                        location</Label>
                                </div>

                                {/* Section pour les photos */}
                                <div>
                                    <Label htmlFor="photos" className="text-sm font-medium">Photos de la Chambre</Label>
                                    <Input
                                        type="file"
                                        id="photos"
                                        name="photos"
                                        multiple
                                        onChange={handleFileChange}
                                        className="mt-1"
                                        accept="image/*"
                                    />
                                    {selectedFiles && selectedFiles.length > 0 && (
                                        <div className="mt-2 text-sm text-gray-600">
                                            **{selectedFiles.length} fichier(s) sélectionné(s) pour l'upload.**
                                        </div>
                                    )}
                                </div>
                                {isEditing && existingMedias.length > 0 && (
                                    <div className="mt-4">
                                        <h4 className="text-md font-medium mb-2">Photos existantes :</h4>
                                        <div className="grid grid-cols-3 gap-2">
                                            {existingMedias.map(media => (
                                                <div key={media.id} className="relative group">
                                                    <img src={media.url} alt={media.description || 'Chambre photo'}
                                                         className="w-full h-24 object-cover rounded-md"/>
                                                    <button
                                                        type="button"
                                                        onClick={() => handleRemoveExistingMedia(media.id)}
                                                        className="absolute top-1 right-1 bg-red-500 text-white rounded-full p-1 text-xs opacity-0 group-hover:opacity-100 transition-opacity"
                                                        title="Supprimer la photo"
                                                    >
                                                        ✕
                                                    </button>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </form>
                        )}
                    </div>
                </ScrollArea>
                <DialogFooter>
                    <DialogClose asChild>
                        <Button variant="outline">Annuler</Button>
                    </DialogClose>
                    <Button
                        type="submit"
                        onClick={handleSubmit}
                        disabled={submitting}
                    >
                        {submitButtonText}
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
};

export default RoomDialog;