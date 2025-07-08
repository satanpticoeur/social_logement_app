import React, {useEffect, useState} from 'react';
import {useParams} from 'react-router-dom';
import type {Contrat, Paiement} from '@/types/common.ts';
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from '@/components/ui/card';
import {Separator} from '@/components/ui/separator';
import {Badge} from '@/components/ui/badge';
import {Button} from '@/components/ui/button';
import {Input} from '@/components/ui/input';
import {Label} from '@/components/ui/label';
import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow} from '@/components/ui/table';
import {toast} from 'sonner';
import {Calendar} from '@/components/ui/calendar';
import {Popover, PopoverContent, PopoverTrigger} from '@/components/ui/popover';
import {format} from 'date-fns';
import {cn} from '@/lib/utils';
// Imports pour la modale d'édition
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";
import {CalendarIcon, PencilIcon, TrashIcon} from "lucide-react";


const ContractDetailPage: React.FC = () => {
    const {id} = useParams<{ id: string }>();
    const [contrat, setContrat] = useState<Contrat | null>(null);
    const [paiements, setPaiements] = useState<Paiement[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    // État du formulaire d'ajout de paiement
    const [newPaymentAmount, setNewPaymentAmount] = useState<string>('');
    const [newPaymentDueDate, setNewPaymentDueDate] = useState<Date | undefined>(undefined);
    const [newPaymentPaidDate, setNewPaymentPaidDate] = useState<Date | undefined>(undefined);
    const [addingPayment, setAddingPayment] = useState<boolean>(false);

    // Nouveaux états pour la modale d'édition de paiement
    const [isEditDialogOpen, setIsEditDialogOpen] = useState<boolean>(false);
    const [editingPayment, setEditingPayment] = useState<Paiement | null>(null);
    const [editAmount, setEditAmount] = useState<string>('');
    const [editDueDate, setEditDueDate] = useState<Date | undefined>(undefined);
    const [editPaidDate, setEditPaidDate] = useState<Date | undefined>(undefined);
    const [isSavingEdit, setIsSavingEdit] = useState<boolean>(false);


    const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

    const fetchContractAndPayments = async () => {
        if (!id) {
            setError("ID de contrat manquant dans l'URL.");
            setLoading(false);
            return;
        }

        try {
            const contractRes = await fetch(`${BACKEND_URL}/api/contrats/${id}`);
            if (!contractRes.ok) {
                if (contractRes.status === 404) {
                    throw new Error("Contrat non trouvé.");
                }
                throw new Error(`Erreur HTTP: ${contractRes.status}`);
            }
            const contractData: Contrat = await contractRes.json();
            setContrat(contractData);

            const paymentsRes = await fetch(`${BACKEND_URL}/api/contrats/${id}/paiements`);
            if (!paymentsRes.ok) {
                throw new Error(`Erreur HTTP lors du chargement des paiements: ${paymentsRes.status}`);
            }
            const paymentsData: Paiement[] = await paymentsRes.json();
            setPaiements(paymentsData);

        } catch (err: unknown) {
            console.error("Erreur lors de la récupération des données:", err);
            if (err instanceof Error) {
                setError(err.message);
                toast.error("Erreur", {
                    description: err.message || "Une erreur est survenue lors du chargement des données.",
                });
            } else {
                setError("Erreur lors du chargement: ");
                toast.error("Erreur", {
                    description: "Une erreur inconnue est survenue lors du chargement des données.",
                });
            }
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchContractAndPayments();
    }, [id, BACKEND_URL]);

    const handleAddPayment = async () => {
        if (!id) return;
        if (!newPaymentAmount || !newPaymentDueDate) {
            toast.error("Erreur", {
                description: "Veuillez entrer un montant et une date d'échéance pour le paiement.",
            });
            return;
        }

        setAddingPayment(true);
        const payload = {
            contrat_id: parseInt(id),
            montant: parseFloat(newPaymentAmount),
            date_echeance: format(newPaymentDueDate, 'yyyy-MM-dd'),
            date_paiement: newPaymentPaidDate ? format(newPaymentPaidDate, 'yyyy-MM-dd') : null,
            statut: newPaymentPaidDate ? 'payé' : 'impayé',
        };

        try {
            const response = await fetch(`${BACKEND_URL}/api/paiements`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || "Échec de l'ajout du paiement.");
            }

            toast.success("Paiement ajouté", {
                description: "Le paiement a été enregistré avec succès.",
            });

            await fetchContractAndPayments();
            setNewPaymentAmount('');
            setNewPaymentDueDate(undefined);
            setNewPaymentPaidDate(undefined);

        } catch (err: unknown) {
            console.error("Erreur lors de l'ajout du paiement:", err);
            if (err instanceof Error) toast.error("Erreur", {
                description: err.message || "Une erreur est survenue lors de l'ajout du paiement.",

            });

        } finally {
            setAddingPayment(false);
        }
    };

    // Fonction pour ouvrir la modale d'édition
    const handleEditClick = (payment: Paiement) => {
        setEditingPayment(payment);
        setEditAmount(payment.montant.toString());
        setEditDueDate(new Date(payment.date_echeance));
        setEditPaidDate(payment.date_paiement ? new Date(payment.date_paiement) : undefined);
        setIsEditDialogOpen(true);
    };

    // Fonction pour sauvegarder les modifications d'un paiement
    const handleSaveEdit = async () => {
        if (!editingPayment) return;

        setIsSavingEdit(true);
        const payload = {
            montant: parseFloat(editAmount),
            date_echeance: format(editDueDate!, 'yyyy-MM-dd'), // ! car on s'attend à ce qu'elle soit définie
            date_paiement: editPaidDate ? format(editPaidDate, 'yyyy-MM-dd') : null,
        };

        try {
            const response = await fetch(`${BACKEND_URL}/api/paiements/${editingPayment.id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || "Échec de la mise à jour du paiement.");
            }

            toast.success("Paiement modifié", {
                description: "Le paiement a été mis à jour avec succès.",
            });

            await fetchContractAndPayments(); // Recharger les données
            setIsEditDialogOpen(false); // Fermer la modale
            setEditingPayment(null); // Réinitialiser l'état
        } catch (err: unknown) {
            console.error("Erreur lors de la mise à jour du paiement:", err);
            if (err instanceof Error)
                toast.error("Erreur", {
                    description: err.message || "Une erreur est survenue lors de la mise à jour du paiement.",
                });
        } finally {
            setIsSavingEdit(false);
        }
    };

    // Fonction pour supprimer un paiement
    const handleDeletePayment = async (paymentId: number) => {
        if (!window.confirm("Êtes-vous sûr de vouloir supprimer ce paiement ? Cette action est irréversible.")) {
            return;
        }

        try {
            const response = await fetch(`${BACKEND_URL}/api/paiements/${paymentId}`, {
                method: 'DELETE',
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || "Échec de la suppression du paiement.");
            }

            toast.success("Paiement supprimé", {
                description: "Le paiement a été supprimé avec succès.",
            });

            await fetchContractAndPayments(); // Recharger les données
        } catch (err: unknown) {
            console.error("Erreur lors de la suppression du paiement:", err);
            if (err instanceof Error) toast.error("Erreur", {
                description: err.message || "Une erreur est survenue lors de la suppression du paiement.",
            });
        }
    };


    if (loading) {
        return <div className="text-center mt-10 text-muted-foreground">Chargement du contrat...</div>;
    }

    if (error) {
        return <div className="text-destructive text-center mt-10">Erreur : {error}</div>;
    }

    if (!contrat) {
        return <div className="text-center mt-10 text-muted-foreground">Aucun contrat trouvé.</div>;
    }

    // Pour le point 2: Mise en évidence des paiements en retard
    const isOverdue = (dueDate: string, paidDate: string | null, status: string): boolean => {
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        const due = new Date(dueDate);
        due.setHours(0, 0, 0, 0);

        // Cas 1: Pas encore payé et date d'échéance passée
        if (status !== 'payé' && due < today) {
            return true;
        }

        // Cas 2: Payé, mais après la date d'échéance (si vous considérez cela comme "en retard")
        if (status === 'payé' && paidDate) {
            const paid = new Date(paidDate);
            paid.setHours(0, 0, 0, 0);
            return paid > due; // Payé APRES la date d'échéance
        }

        return false; // Ni impayé et en retard, ni payé tardivement
    };


    return (
        <div className="p-4 bg-background text-foreground max-w-4xl mx-auto">
            <Card className="shadow-lg border-border">
                <CardHeader>
                    <CardTitle className="text-3xl font-bold text-primary">Détails du Contrat #{contrat.id}</CardTitle>
                    <CardDescription className="text-muted-foreground">
                        Contrat pour la chambre <span
                        className="font-semibold text-foreground">{contrat.chambre?.titre || 'N/A'}</span>
                    </CardDescription>
                </CardHeader>
                <CardContent className="grid gap-6">
                    {/* Informations Générales du Contrat */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <p className="text-sm font-medium text-muted-foreground">Période du Contrat</p>
                            <p className="text-lg">
                                Du <span
                                className="font-semibold">{new Date(contrat.date_debut).toLocaleDateString()}</span> au <span
                                className="font-semibold">{new Date(contrat.date_fin).toLocaleDateString()}</span>
                            </p>
                        </div>
                        <div>
                            <p className="text-sm font-medium text-muted-foreground">Montant de la Caution</p>
                            <p className="text-lg font-semibold">{parseFloat(contrat.montant_caution).toLocaleString()} XOF
                                ({contrat.mois_caution} mois)</p>
                        </div>
                        <div>
                            <p className="text-sm font-medium text-muted-foreground">Mode de Paiement</p>
                            <p className="text-lg font-semibold capitalize">{contrat.mode_paiement || 'N/A'}</p>
                        </div>
                        <div>
                            <p className="text-sm font-medium text-muted-foreground">Périodicité</p>
                            <Badge className="text-lg capitalize">{contrat.periodicite || 'N/A'}</Badge>
                        </div>
                        <div>
                            <p className="text-sm font-medium text-muted-foreground">Statut du Contrat</p>
                            <Badge variant={contrat.statut === 'actif' ? 'default' : 'secondary'}
                                   className="text-lg capitalize">
                                {contrat.statut || 'N/A'}
                            </Badge>
                        </div>
                    </div>

                    {/* Nouveaux champs pour le solde */}
                    <Separator/>
                    <div
                        className="grid grid-cols-1 md:grid-cols-3 gap-4 bg-accent/20 p-4 rounded-md border border-accent">
                        <div>
                            <p className="text-sm font-medium text-muted-foreground">Montant Total Attendu</p>
                            <p className="text-lg font-bold text-green-600">
                                {contrat.total_expected_amount?.toLocaleString() || 'N/A'} XOF
                            </p>
                        </div>
                        <div>
                            <p className="text-sm font-medium text-muted-foreground">Montant Total Payé</p>
                            <p className="text-lg font-bold text-green-600">
                                {contrat.total_paid_amount?.toLocaleString() || 'N/A'} XOF
                            </p>
                        </div>
                        <div>
                            <p className="text-sm font-medium text-muted-foreground">Solde Restant Dû</p>
                            <p className={cn(
                                "text-lg font-bold",
                                contrat.remaining_balance && contrat.remaining_balance > 0 ? "text-red-600" : "text-green-600"
                            )}>
                                {contrat.remaining_balance?.toLocaleString() || 'N/A'} XOF
                            </p>
                        </div>
                    </div>
                    {/* Fin des nouveaux champs pour le solde */}


                    {contrat.description && (
                        <>
                            <Separator/>
                            <div>
                                <p className="text-sm font-medium text-muted-foreground">Description du Contrat</p>
                                <p className="text-lg">{contrat.description}</p>
                            </div>
                        </>
                    )}

                    <Separator/>

                    {/* Informations du Locataire */}
                    <div>
                        <h3 className="text-xl font-semibold mb-3 text-secondary-foreground">Informations du
                            Locataire</h3>
                        {contrat.locataire ? (
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <p className="text-sm font-medium text-muted-foreground">Nom d'utilisateur</p>
                                    <p className="text-lg font-semibold">{contrat.locataire.nom_utilisateur}</p>
                                </div>
                                <div>
                                    <p className="text-sm font-medium text-muted-foreground">Email</p>
                                    <p className="text-lg">{contrat.locataire.email}</p>
                                </div>
                                <div>
                                    <p className="text-sm font-medium text-muted-foreground">Téléphone</p>
                                    <p className="text-lg">{contrat.locataire.telephone}</p>
                                </div>
                                <div>
                                    <p className="text-sm font-medium text-muted-foreground">CNI</p>
                                    <p className="text-lg">{contrat.locataire.cni}</p>
                                </div>
                            </div>
                        ) : (
                            <p className="text-muted-foreground">Aucune information de locataire disponible.</p>
                        )}
                    </div>

                    <Separator/>

                    {/* Informations de la Chambre */}
                    <div>
                        <h3 className="text-xl font-semibold mb-3 text-secondary-foreground">Informations de la
                            Chambre</h3>
                        {contrat.chambre ? (
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <p className="text-sm font-medium text-muted-foreground">Titre de la Chambre</p>
                                    <p className="text-lg font-semibold">{contrat.chambre.titre}</p>
                                </div>
                                <div>
                                    <p className="text-sm font-medium text-muted-foreground">Prix</p>
                                    <p className="text-lg">{parseFloat(String(contrat.chambre.prix)).toLocaleString()} XOF</p>
                                </div>
                                <div>
                                    <p className="text-sm font-medium text-muted-foreground">Type / Taille</p>
                                    <p className="text-lg capitalize">{contrat.chambre.type} ({contrat.chambre.taille})</p>
                                </div>
                                <div>
                                    <p className="text-sm font-medium text-muted-foreground">Meublée</p>
                                    <p className="text-lg">{contrat.chambre.meublee ? 'Oui' : 'Non'}</p>
                                </div>
                                <div>
                                    <p className="text-sm font-medium text-muted-foreground">Salle de bain</p>
                                    <p className="text-lg">{contrat.chambre.salle_de_bain ? 'Oui' : 'Non'}</p>
                                </div>
                                {contrat.chambre.maison && (
                                    <div>
                                        <p className="text-sm font-medium text-muted-foreground">Adresse de la
                                            Maison</p>
                                        <p className="text-lg font-semibold">{contrat.chambre.maison.adresse}</p>
                                    </div>
                                )}
                            </div>
                        ) : (
                            <p className="text-muted-foreground">Aucune information de chambre disponible.</p>
                        )}
                    </div>

                    <Separator className="my-8"/>

                    {/* Section Paiements */}
                    <div>
                        <h2 className="text-2xl font-bold mb-4 text-primary">Gestion des Paiements</h2>

                        {/* Formulaire d'ajout de paiement */}
                        <Card className="mb-6 bg-secondary/10 border-secondary">
                            <CardHeader>
                                <CardTitle className="text-xl">Ajouter un Nouveau Paiement</CardTitle>
                            </CardHeader>
                            <CardContent className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                <div>
                                    <Label htmlFor="newPaymentAmount">Montant</Label>
                                    <Input
                                        id="newPaymentAmount"
                                        type="number"
                                        value={newPaymentAmount}
                                        onChange={(e) => setNewPaymentAmount(e.target.value)}
                                        placeholder="Ex: 250000"
                                        step="0.01"
                                    />
                                </div>
                                <div>
                                    <Label htmlFor="newPaymentDueDate">Date d'échéance</Label>
                                    <Popover>
                                        <PopoverTrigger asChild>
                                            <Button
                                                variant={"outline"}
                                                className={cn(
                                                    "w-full justify-start text-left font-normal",
                                                    !newPaymentDueDate && "text-muted-foreground"
                                                )}
                                            >
                                                <CalendarIcon className="mr-2 h-4 w-4"/>
                                                {newPaymentDueDate ? format(newPaymentDueDate, "PPP") :
                                                    <span>Choisir la date d'échéance</span>}
                                            </Button>
                                        </PopoverTrigger>
                                        <PopoverContent className="w-auto p-0" align="start">
                                            <Calendar
                                                mode="single"
                                                selected={newPaymentDueDate}
                                                onSelect={setNewPaymentDueDate}
                                                initialFocus
                                            />
                                        </PopoverContent>
                                    </Popover>
                                </div>
                                <div>
                                    <Label htmlFor="newPaymentPaidDate">Date de Paiement (optionnel)</Label>
                                    <Popover>
                                        <PopoverTrigger asChild>
                                            <Button
                                                variant={"outline"}
                                                className={cn(
                                                    "w-full justify-start text-left font-normal",
                                                    !newPaymentPaidDate && "text-muted-foreground"
                                                )}
                                            >
                                                <CalendarIcon className="mr-2 h-4 w-4"/>
                                                {newPaymentPaidDate ? format(newPaymentPaidDate, "PPP") :
                                                    <span>Choisir la date de paiement</span>}
                                            </Button>
                                        </PopoverTrigger>
                                        <PopoverContent className="w-auto p-0" align="start">
                                            <Calendar
                                                mode="single"
                                                selected={newPaymentPaidDate}
                                                onSelect={setNewPaymentPaidDate}
                                                initialFocus
                                            />
                                        </PopoverContent>
                                    </Popover>
                                </div>
                                <div className="md:col-span-2 lg:col-span-3 flex justify-end">
                                    <Button onClick={handleAddPayment} disabled={addingPayment}>
                                        {addingPayment ? "Ajout en cours..." : "Enregistrer Paiement"}
                                    </Button>
                                </div>
                            </CardContent>
                        </Card>

                        {/* Liste des paiements existants */}
                        <h3 className="text-xl font-semibold mb-3 text-secondary-foreground">Historique des
                            Paiements</h3>
                        {paiements.length > 0 ? (
                            <Table className="bg-card rounded-lg shadow-sm border border-border">
                                <TableHeader>
                                    <TableRow>
                                        <TableHead>ID</TableHead>
                                        <TableHead>Montant</TableHead>
                                        <TableHead>Date Échéance</TableHead>
                                        <TableHead>Date Paiement</TableHead>
                                        <TableHead>Statut</TableHead>
                                        <TableHead>Créé le</TableHead>
                                        <TableHead className="text-right">Actions</TableHead> {/* Nouvelle colonne */}
                                    </TableRow>
                                </TableHeader>
                                <TableBody>
                                    {paiements.map(paiement => (
                                        <TableRow
                                            key={paiement.id}
                                            className={cn(
                                                "hover:bg-muted/50",
                                                isOverdue(paiement.date_echeance, paiement.date_paiement, paiement.statut) && "bg-red-50/50 border-l-4 border-red-500"
                                            )}
                                        >
                                            <TableCell className="font-medium">{paiement.id}</TableCell>
                                            <TableCell>{paiement.montant.toLocaleString()} XOF</TableCell>
                                            <TableCell>{new Date(paiement.date_echeance).toLocaleDateString()}</TableCell>
                                            <TableCell>
                                                {paiement.date_paiement ? new Date(paiement.date_paiement).toLocaleDateString() :
                                                    <span className="text-muted-foreground">N/A</span>}
                                            </TableCell>
                                            <TableCell>
                                                <Badge variant={paiement.statut === 'payé' ? 'default' : 'destructive'}
                                                       className="capitalize">
                                                    {paiement.statut}
                                                </Badge>
                                            </TableCell>
                                            <TableCell>{new Date(paiement.cree_le).toLocaleDateString()}</TableCell>
                                            <TableCell className="text-right">
                                                <div className="flex justify-end gap-2">
                                                    <Button variant="outline" size="icon"
                                                            onClick={() => handleEditClick(paiement)}>
                                                        <PencilIcon className="h-4 w-4"/>
                                                    </Button>
                                                    <Button variant="destructive" size="icon"
                                                            onClick={() => handleDeletePayment(paiement.id)}>
                                                        <TrashIcon className="h-4 w-4"/>
                                                    </Button>
                                                </div>
                                            </TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        ) : (
                            <p className="text-center text-muted-foreground mt-4">Aucun paiement enregistré pour ce
                                contrat.</p>
                        )}
                    </div>
                </CardContent>
            </Card>

            {/* Modale d'édition de paiement */}
            <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
                <DialogContent className="sm:max-w-[425px]">
                    <DialogHeader>
                        <DialogTitle>Modifier le Paiement</DialogTitle>
                        <DialogDescription>
                            Apportez des modifications au paiement. Cliquez sur Enregistrer lorsque vous avez terminé.
                        </DialogDescription>
                    </DialogHeader>
                    <div className="grid gap-4 py-4">
                        <div className="grid grid-cols-4 items-center gap-4">
                            <Label htmlFor="editAmount" className="text-right">
                                Montant
                            </Label>
                            <Input
                                id="editAmount"
                                type="number"
                                value={editAmount}
                                onChange={(e) => setEditAmount(e.target.value)}
                                className="col-span-3"
                                step="0.01"
                            />
                        </div>
                        <div className="grid grid-cols-4 items-center gap-4">
                            <Label htmlFor="editDueDate" className="text-right">
                                Date d'échéance
                            </Label>
                            <Popover>
                                <PopoverTrigger asChild>
                                    <Button
                                        variant={"outline"}
                                        className={cn(
                                            "col-span-3 justify-start text-left font-normal",
                                            !editDueDate && "text-muted-foreground"
                                        )}
                                    >
                                        <CalendarIcon className="mr-2 h-4 w-4"/>
                                        {editDueDate ? format(editDueDate, "PPP") : <span>Choisir la date</span>}
                                    </Button>
                                </PopoverTrigger>
                                <PopoverContent className="w-auto p-0">
                                    <Calendar
                                        mode="single"
                                        selected={editDueDate}
                                        onSelect={setEditDueDate}
                                        initialFocus
                                    />
                                </PopoverContent>
                            </Popover>
                        </div>
                        <div className="grid grid-cols-4 items-center gap-4">
                            <Label htmlFor="editPaidDate" className="text-right">
                                Date de Paiement
                            </Label>
                            <Popover>
                                <PopoverTrigger asChild>
                                    <Button
                                        variant={"outline"}
                                        className={cn(
                                            "col-span-3 justify-start text-left font-normal",
                                            !editPaidDate && "text-muted-foreground"
                                        )}
                                    >
                                        <CalendarIcon className="mr-2 h-4 w-4"/>
                                        {editPaidDate ? format(editPaidDate, "PPP") :
                                            <span>Choisir la date (optionnel)</span>}
                                    </Button>
                                </PopoverTrigger>
                                <PopoverContent className="w-auto p-0">
                                    <Calendar
                                        mode="single"
                                        selected={editPaidDate}
                                        onSelect={setEditPaidDate}
                                        initialFocus
                                    />
                                </PopoverContent>
                            </Popover>
                        </div>
                    </div>
                    <DialogFooter>
                        <Button onClick={handleSaveEdit} disabled={isSavingEdit}>
                            {isSavingEdit ? "Enregistrement..." : "Enregistrer les modifications"}
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
            {/* Fin Modale d'édition */}

        </div>
    );
};

export default ContractDetailPage;