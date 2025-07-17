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
import { Badge } from "@/components/ui/badge.tsx";
import { format } from 'date-fns';

interface ContratLocataire {
    id: number;
    chambre_id: number;
    chambre_titre: string;
    proprietaire_nom: string;
    date_debut: string;
    date_fin: string;
    montant_caution: number;
    duree_mois: number;
    statut: string; // Should be 'en_attente_validation' for this page
}

const LodgerPendingRequestsPage: React.FC = () => {
    const [demandesEnAttente, setDemandesEnAttente] = useState<ContratLocataire[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchDemandesEnAttente();
    }, []);

    const fetchDemandesEnAttente = async () => {
        setLoading(true);
        try {
            // Nouvelle route backend pour les demandes en attente
            const data: ContratLocataire[] = await authenticatedFetch('locataire/mes-demandes-en-attente', { method: 'GET' });
            setDemandesEnAttente(data);
            toast.success(`${data.length} demandes en attente chargées.`);
        } catch (error: any) {
            console.error('Erreur lors du chargement des demandes en attente:', error);
            toast.error("Échec du chargement des demandes.", { description: error.message || "Erreur inconnue." });
        } finally {
            setLoading(false);
        }
    };

    const getStatusBadgeVariant = (status: string) => {
        return status === 'en_attente_validation' ? 'secondary' : 'default';
    };

    if (loading) {
        return <div className="text-center p-8">Chargement de vos demandes en attente...</div>;
    }

    return (
        <div className="container mx-auto p-4">
            <h1 className="text-3xl font-bold mb-6 text-center">Mes Demandes de Location en Attente</h1>

            {demandesEnAttente.length === 0 ? (
                <div className="text-center p-8 text-gray-600 border rounded-lg">
                    <p className="text-lg">Vous n'avez aucune demande de location en attente pour le moment.</p>
                </div>
            ) : (
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>Chambre</TableHead>
                            <TableHead>Propriétaire</TableHead>
                            <TableHead>Date Début</TableHead>
                            <TableHead>Durée</TableHead>
                            <TableHead>Caution</TableHead>
                            <TableHead>Statut</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {demandesEnAttente.map((contrat) => (
                            <TableRow key={contrat.id}>
                                <TableCell className="font-medium">{contrat.chambre_titre}</TableCell>
                                <TableCell>{contrat.proprietaire_nom || 'N/A'}</TableCell>
                                <TableCell>{format(new Date(contrat.date_debut), 'dd/MM/yyyy')}</TableCell>
                                <TableCell>{contrat.duree_mois} mois</TableCell>
                                <TableCell>{contrat.montant_caution.toLocaleString()} FCFA</TableCell>
                                <TableCell>
                                    <Badge variant={getStatusBadgeVariant(contrat.statut)} className="bg-yellow-100 text-yellow-800">
                                        {contrat.statut.replace(/_/g, ' ')}
                                    </Badge>
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            )}
        </div>
    );
};

export default LodgerPendingRequestsPage;