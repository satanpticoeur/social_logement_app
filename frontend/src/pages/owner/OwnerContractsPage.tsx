// src/pages/ProprietaireContratsPage.tsx (No changes needed if backend sends all statuses)

import React, {useEffect, useState} from 'react';
import {authenticatedFetch} from '@/lib/api';
import {toast} from 'sonner';
import {Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle} from "@/components/ui/card";
import {Badge} from "@/components/ui/badge";
import {Button} from "@/components/ui/button";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    // DialogTrigger
} from "@/components/ui/dialog";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow
} from "@/components/ui/table.tsx";
import {ScrollArea} from "@/components/ui/scroll-area.tsx";

interface ContratProprietaire {
    id: number;
    locataire_id: number;
    locataire_nom_utilisateur: string;
    locataire_email: string;
    chambre_id: number;
    chambre_titre: string;
    chambre_adresse: string;
    prix_mensuel_chambre: number;
    date_debut: string;
    date_fin: string;
    montant_caution: number | null;
    mois_caution: number | null;
    mode_paiement: string;
    periodicite: string;
    statut: string; // Can be 'actif', 'rejete', 'resilié', 'termine'
    description: string | null;
    cree_le: string;
    paiements?: PaiementContrat[];
}

interface PaiementContrat {
    id: number;
    montant: number;
    date_echeance: string;
    statut: string; // 'paye', 'impaye', 'en_retard'
    description: string;
    date_paiement: string | null;
}


const ProprietaireContratsPage: React.FC = () => {
    const [contrats, setContrats] = useState<ContratProprietaire[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedContrat, setSelectedContrat] = useState<ContratProprietaire | null>(null);
    const [showContratDetailsDialog, setShowContratDetailsDialog] = useState(false);
    const [loadingContratDetails, setLoadingContratDetails] = useState(false);
    const [isResiliating, setIsResiliating] = useState(false);

    useEffect(() => {
        fetchContrats();
    }, []);

    const fetchContrats = async () => {
        setLoading(true);
        try {
            // This backend endpoint should now return all relevant contracts for the owner,
            // excluding 'en_attente_validation' which are handled by OwnerRentalRequestsPage.
            // Example: active, rejected, terminated, re_siliated.
            const data: ContratProprietaire[] = await authenticatedFetch('proprietaire/contrats', {method: 'GET'});
            setContrats(data);
            toast.success(`${data.length} contrats chargés.`);
        } catch (error: any) {
            console.error('Erreur lors du chargement des contrats:', error);
            toast.error("Échec du chargement des contrats.", {description: error.message || "Erreur inconnue."});
        } finally {
            setLoading(false);
        }
    };

    const fetchContratDetails = async (contratId: number) => {
        setLoadingContratDetails(true);
        try {
            const data: ContratProprietaire = await authenticatedFetch(`proprietaire/contrats/${contratId}/details`, {method: 'GET'});
            setSelectedContrat(data);
            setShowContratDetailsDialog(true);
            toast.success("Détails du contrat chargés.");
        } catch (error: any) {
            console.error('Erreur lors du chargement des détails du contrat:', error);
            toast.error("Échec du chargement des détails.", {description: error.message || "Erreur inconnue."});
        } finally {
            setLoadingContratDetails(false);
        }
    };

    const handleResilierContrat = async () => {
        if (!selectedContrat || !confirm("Êtes-vous sûr de vouloir résilier ce contrat ? Cette action est irréversible.")) {
            return;
        }

        setIsResiliating(true);
        try {
            const response = await authenticatedFetch(`proprietaire/contrats/${selectedContrat.id}/resilier`, {
                method: 'PUT',
            });
            console.log("Réponse résiliation contrat:", response);
            toast.success("Contrat résilié avec succès !");
            setShowContratDetailsDialog(false);
            fetchContrats(); // Refresh the list
        } catch (error: any) {
            console.error('Erreur lors de la résiliation du contrat:', error);
            toast.error("Échec de la résiliation du contrat.", {description: error.message || "Erreur inconnue."});
        } finally {
            setIsResiliating(false);
        }
    };

    const getStatusBadgeVariant = (status: string) => {
        switch (status) {
            case 'actif':
                return 'default';
            case 'rejete':
                return 'destructive';
            case 'resilié':
                return 'destructive';
            case 'termine':
                return 'secondary';
            case 'en_attente_validation':
                return 'outline'; // Should not appear here if backend is correct
            default:
                return 'outline';
        }
    };

    const getPaiementStatusBadgeVariant = (status: string) => {
        switch (status) {
            case 'paye':
                return 'default';
            case 'impaye':
                return 'secondary';
            case 'en_retard':
                return 'destructive';
            default:
                return 'secondary';
        }
    };


    if (loading) {
        return <div className="text-center p-4">Chargement de vos contrats...</div>;
    }

    // Filter out 'en_attente_validation' contracts on the frontend as a safeguard,
    // though the backend endpoint should primarily handle this.
    const displayContracts = contrats.filter(c => c.statut !== 'en_attente_validation');


    return (
        <div className="container mx-auto p-4">
            <h1 className="text-3xl font-bold mb-6 text-center">Vos Contrats de Location</h1>

            {displayContracts.length === 0 ? (
                <p className="text-center text-lg text-gray-600">Vous n'avez aucun contrat actif, rejeté ou terminé pour
                    le moment.</p>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {displayContracts.map((contrat) => (
                        <Card key={contrat.id} className="flex flex-col">
                            <CardHeader>
                                <CardTitle>{contrat.chambre_titre}</CardTitle>
                                <CardDescription>Locataire: {contrat.locataire_nom_utilisateur} ({contrat.locataire_email})</CardDescription>
                                <CardDescription>{contrat.chambre_adresse}</CardDescription>
                            </CardHeader>
                            <CardContent className="flex-grow">
                                <p className="mb-2"><strong>Statut:</strong> <Badge
                                    variant={getStatusBadgeVariant(contrat.statut)}
                                    className="ml-2">{contrat.statut.replace('_', ' ')}</Badge></p>
                                <p className="mb-1">
                                    <strong>Début:</strong> {new Date(contrat.date_debut).toLocaleDateString()}</p>
                                <p className="mb-1">
                                    <strong>Fin:</strong> {new Date(contrat.date_fin).toLocaleDateString()}</p>
                                <p className="mb-1"><strong>Loyer
                                    Mensuel:</strong> {contrat.prix_mensuel_chambre.toLocaleString()} FCFA</p>
                                {contrat.montant_caution && (
                                    <p className="mb-1">
                                        <strong>Caution:</strong> {contrat.montant_caution.toLocaleString()} FCFA
                                        ({contrat.mois_caution} mois)</p>
                                )}
                                <p className="mb-1"><strong>Périodicité:</strong> {contrat.periodicite}</p>
                                <p className="mb-1"><strong>Mode de Paiement:</strong> {contrat.mode_paiement}</p>
                                {contrat.description && (
                                    <p className="mt-3 text-sm text-gray-600">
                                        <strong>Description:</strong> "{contrat.description}"</p>
                                )}
                            </CardContent>
                            <CardFooter className="flex justify-end">
                                <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => fetchContratDetails(contrat.id)}
                                    disabled={loadingContratDetails}
                                >
                                    {loadingContratDetails && selectedContrat?.id === contrat.id ? 'Chargement...' : 'Gérer le contrat'}
                                </Button>
                            </CardFooter>
                        </Card>
                    ))}
                </div>
            )}

            <Dialog open={showContratDetailsDialog} onOpenChange={setShowContratDetailsDialog}>
                <DialogContent className="sm:max-w-[700px]">
                    <DialogHeader>
                        <DialogTitle>Détails du Contrat</DialogTitle>
                        <DialogDescription>
                            Informations complètes et options de gestion pour le contrat.
                        </DialogDescription>
                    </DialogHeader>
                    <ScrollArea className="max-h-[70vh] py-4">
                        {selectedContrat ? (
                            <div className="py-4 space-y-4">
                                <p>
                                    <strong>Chambre:</strong> {selectedContrat.chambre_titre} ({selectedContrat.chambre_adresse})
                                </p>
                                <p>
                                    <strong>Locataire:</strong> {selectedContrat.locataire_nom_utilisateur} ({selectedContrat.locataire_email})
                                </p>
                                <p><strong>Statut:</strong> <Badge
                                    variant={getStatusBadgeVariant(selectedContrat.statut)}>{selectedContrat.statut.replace('_', ' ')}</Badge>
                                </p>
                                <p>
                                    <strong>Période:</strong> Du {new Date(selectedContrat.date_debut).toLocaleDateString()} au {new Date(selectedContrat.date_fin).toLocaleDateString()}
                                </p>
                                <p><strong>Loyer
                                    Mensuel:</strong> {selectedContrat.prix_mensuel_chambre.toLocaleString()} FCFA</p>
                                <p>
                                    <strong>Caution:</strong> {selectedContrat.montant_caution?.toLocaleString() || 'N/A'} FCFA
                                    ({selectedContrat.mois_caution} mois)</p>
                                <p><strong>Mode de Paiement:</strong> {selectedContrat.mode_paiement}</p>
                                <p><strong>Périodicité:</strong> {selectedContrat.periodicite}</p>
                                {selectedContrat.description &&
                                    <p><strong>Description:</strong> {selectedContrat.description}</p>}

                                {selectedContrat.paiements && selectedContrat.paiements.length > 0 && (
                                    <div className="mt-6">
                                        <h3 className="text-lg font-semibold mb-2">Échéancier des Paiements</h3>
                                        <Table>
                                            <TableHeader>
                                                <TableRow>
                                                    <TableHead>Description</TableHead>
                                                    <TableHead>Montant</TableHead>
                                                    <TableHead>Échéance</TableHead>
                                                    <TableHead>Date Payé</TableHead>
                                                    <TableHead>Statut</TableHead>
                                                </TableRow>
                                            </TableHeader>
                                            <TableBody>
                                                {selectedContrat.paiements.map(paiement => (
                                                    <TableRow key={paiement.id}>
                                                        <TableCell>{paiement.description}</TableCell>
                                                        <TableCell>{paiement.montant.toLocaleString()} FCFA</TableCell>
                                                        <TableCell>{new Date(paiement.date_echeance).toLocaleDateString()}</TableCell>
                                                        <TableCell>{paiement.date_paiement ? new Date(paiement.date_paiement).toLocaleDateString() : 'N/A'}</TableCell>
                                                        <TableCell>
                                                            <Badge
                                                                variant={getPaiementStatusBadgeVariant(paiement.statut)}>
                                                                {paiement.statut.replace('_', ' ')}
                                                            </Badge>
                                                        </TableCell>
                                                    </TableRow>
                                                ))}
                                            </TableBody>
                                        </Table>
                                    </div>
                                )}

                            </div>
                        ) : (
                            <div className="text-center p-4">Chargement des détails...</div>
                        )}
                    </ScrollArea>
                    <DialogFooter className="mt-4 flex justify-between">
                        {selectedContrat?.statut === 'actif' && (
                            <Button
                                variant="destructive"
                                onClick={handleResilierContrat}
                                disabled={isResiliating}
                            >
                                {isResiliating ? 'Résililiation en cours...' : 'Résilier le contrat'}
                            </Button>
                        )}
                        <Button variant="secondary" onClick={() => setShowContratDetailsDialog(false)}>
                            Fermer
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    );
};

export default ProprietaireContratsPage;