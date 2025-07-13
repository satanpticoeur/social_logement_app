import React, { useEffect, useState } from 'react';
import { authenticatedFetch } from '@/lib/api.ts';
import { toast } from 'sonner';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table.tsx";
import { Button } from "@/components/ui/button.tsx";
import { Badge } from "@/components/ui/badge.tsx";
import { format } from 'date-fns';
import { CheckCircle2, XCircle } from 'lucide-react';

interface ContratDemande {
    id: number;
    locataire_id: number;
    locataire_nom: string;
    chambre_id: number;
    chambre_titre: string;
    date_debut: string;
    date_fin: string;
    montant_caution: number;
    duree_mois: number;
    statut: string; // 'en_attente_validation', 'actif', 'rejete'
}

const OwnerRentalRequestsPage: React.FC = () => {
    const [demandes, setDemandes] = useState<ContratDemande[]>([]);
    const [loading, setLoading] = useState(true);
    const [processingId, setProcessingId] = useState<number | null>(null); // Pour désactiver le bouton pendant le traitement

    useEffect(() => {
        fetchDemandesEnAttente();
    }, []);

    const fetchDemandesEnAttente = async () => {
        setLoading(true);
        try {
            const data: ContratDemande[] = await authenticatedFetch('proprietaire/demandes-location-en-attente', { method: 'GET' });
            setDemandes(data);
            toast.success("Demandes de location chargées.");
        } catch (error: any) {
            console.error('Erreur lors du chargement des demandes de location:', error);
            toast.error("Échec du chargement des demandes.", { description: error.message || "Erreur inconnue." });
        } finally {
            setLoading(false);
        }
    };

    const handleActionContrat = async (contratId: number, action: 'approuver' | 'rejeter') => {
        setProcessingId(contratId);
        try {
            // Les routes PUT que nous avons déjà définies dans le backend
            const response = await authenticatedFetch(`proprietaire/contrats/${contratId}/${action}`, {
                method: 'PUT',
            });
            console.log(`Réponse ${action} contrat:`, response);
            toast.success(`Demande ${action === 'approuver' ? 'approuvée' : 'rejetée'} avec succès !`);
            // Mettre à jour la liste en retirant la demande traitée ou en rafraîchissant
            setDemandes(prevDemandes => prevDemandes.filter(demande => demande.id !== contratId));
        } catch (error: any) {
            console.error(`Erreur lors de l'action ${action} sur le contrat:`, error);
            toast.error(`Échec de l'action ${action}.`, { description: error.message || "Erreur inconnue." });
        } finally {
            setProcessingId(null);
        }
    };

    if (loading) {
        return <div className="text-center p-8">Chargement des demandes de location...</div>;
    }

    return (
        <div className="container mx-auto p-4">
            <h1 className="text-3xl font-bold mb-6 text-center">Demandes de Location en Attente</h1>

            {demandes.length === 0 ? (
                <div className="text-center p-8 text-gray-600 border rounded-lg">
                    <p className="text-lg">Aucune nouvelle demande de location en attente pour le moment.</p>
                </div>
            ) : (
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>Locataire</TableHead>
                            <TableHead>Chambre</TableHead>
                            <TableHead>Date Début</TableHead>
                            <TableHead>Durée</TableHead>
                            <TableHead>Caution Est.</TableHead>
                            <TableHead>Statut</TableHead>
                            <TableHead className="text-right">Actions</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {demandes.map((demande) => (
                            <TableRow key={demande.id}>
                                <TableCell className="font-medium">{demande.locataire_nom}</TableCell>
                                <TableCell>{demande.chambre_titre}</TableCell>
                                <TableCell>{format(new Date(demande.date_debut), 'dd/MM/yyyy')}</TableCell>
                                <TableCell>{demande.duree_mois} mois</TableCell>
                                <TableCell>{demande.montant_caution.toLocaleString()} FCFA</TableCell>
                                <TableCell>
                                    <Badge variant="outline" className="bg-yellow-100 text-yellow-800">
                                        {demande.statut.replace(/_/g, ' ')}
                                    </Badge>
                                </TableCell>
                                <TableCell className="text-right">
                                    <Button
                                        variant="ghost"
                                        size="sm"
                                        className="text-green-600 hover:text-green-800"
                                        onClick={() => handleActionContrat(demande.id, 'approuver')}
                                        disabled={processingId === demande.id}
                                    >
                                        <CheckCircle2 className="h-5 w-5" />
                                        <span className="sr-only">Approuver</span>
                                    </Button>
                                    <Button
                                        variant="ghost"
                                        size="sm"
                                        className="text-red-600 hover:text-red-800 ml-2"
                                        onClick={() => handleActionContrat(demande.id, 'rejeter')}
                                        disabled={processingId === demande.id}
                                    >
                                        <XCircle className="h-5 w-5" />
                                        <span className="sr-only">Rejeter</span>
                                    </Button>
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            )}
        </div>
    );
};

export default OwnerRentalRequestsPage;