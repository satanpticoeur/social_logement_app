import React, {type ReactNode, useEffect, useState} from 'react';
import {authenticatedFetch} from '@/lib/api';
import {toast} from 'sonner';

import {
    Dialog,
    DialogClose,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger
} from "@/components/ui/dialog";
import {Button} from "@/components/ui/button";
import {Label} from "@/components/ui/label";
import {Input} from "@/components/ui/input";
import {Textarea} from "@/components/ui/textarea";
import {ScrollArea} from "@/components/ui/scroll-area";

interface Maison {
    id: number;
    adresse: string;
    ville: string;
    description: string | null;
}

interface HouseDialogFormProps {
    onHouseActionSuccess: () => void;
    houseToEdit?: Maison | null;
    actionType: 'add' | 'edit';
    children: ReactNode;
}

export const HouseDialogForm: React.FC<HouseDialogFormProps> = (
    {
        onHouseActionSuccess,
        houseToEdit,
        actionType,
        children
    }) => {
    const [formData, setFormData] = useState({
        adresse: '',
        ville: '',
        description: '',
    });
    const [submitting, setSubmitting] = useState(false);
    const [dialogOpen, setDialogOpen] = useState(false);

    const isEditing = actionType === 'edit';
    const dialogTitle = isEditing ? "Modifier la Maison" : "Ajouter une Nouvelle Maison";
    const submitButtonText = isEditing ? (submitting ? 'Mise à jour...' : 'Mettre à jour la maison') : (submitting ? 'Ajout en cours...' : 'Ajouter la maison');

    useEffect(() => {
        if (dialogOpen) {
            if (isEditing && houseToEdit) {
                setFormData({
                    adresse: houseToEdit.adresse,
                    ville: houseToEdit.ville,
                    description: houseToEdit.description || '', // Gérer les nulls
                });
            } else {
                // Réinitialise le formulaire en mode ajout
                setFormData({
                    adresse: '',
                    ville: '',
                    description: '',
                });
            }
        }
    }, [dialogOpen, isEditing, houseToEdit]);

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        const {name, value} = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value,
        }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setSubmitting(true);
        try {
            let response;
            if (isEditing && houseToEdit) {
                // Mode modification
                response = await authenticatedFetch(`maisons/${houseToEdit.id}`, {
                    method: 'PUT',
                    body: JSON.stringify(formData),
                });
                toast.success(response.message || "Maison mise à jour avec succès !");
            } else {
                // Mode ajout
                response = await authenticatedFetch('proprietaire/maisons', {
                    method: 'POST',
                    body: JSON.stringify(formData),
                });
                toast.success(response.message || "Maison ajoutée avec succès !");
            }

            onHouseActionSuccess();
            setDialogOpen(false);

        } catch (error: any) {
            console.error(`Erreur lors de ${isEditing ? 'la modification' : 'l\'ajout'} de la maison:`, error);
            toast.error(`Échec de ${isEditing ? 'la modification' : 'l\'ajout'} de la maison.`, {description: error.message || "Erreur inconnue."});
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
                        {isEditing ? "Modifiez les informations de la maison." : "Remplissez les informations de la maison à ajouter."}
                    </DialogDescription>
                </DialogHeader>
                <ScrollArea className="max-h-[70vh] p-4">
                    <div className="mt-9 p-4">
                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div>
                                <Label htmlFor="adresse" className="text-sm font-medium">Adresse</Label>
                                <Input type="text" id="adresse" name="adresse" value={formData.adresse}
                                       onChange={handleInputChange} required className="mt-1 "/>
                            </div>
                            <div>
                                <Label htmlFor="ville" className="text-sm font-medium">Ville</Label>
                                <Input type="text" id="ville" name="ville" value={formData.ville}
                                       onChange={handleInputChange} required className="mt-1 "/>
                            </div>
                            <div>
                                <Label htmlFor="description" className="text-sm font-medium">Description
                                    (optionnel)</Label>
                                <Textarea id="description" name="description" value={formData.description}
                                          onChange={handleInputChange} rows={3} className="mt-1 "></Textarea>
                            </div>
                        </form>
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

