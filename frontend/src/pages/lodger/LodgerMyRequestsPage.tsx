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
    chambre_titre: string; // Titre de la chambre associée
    proprietaire_nom: string; // Nom du propriétaire (si disponible via l'API)
    date_debut: string;
    date_fin: string;
    montant_caution: number;
    duree_mois: number;
    statut: string; // 'en_attente_validation', 'actif', 'rejete', 'termine'
}

const LodgerMyRequestsPage: React.FC = () => {
    const [mesDemandes, setMesDemandes] = useState<ContratLocataire[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchMesDemandes();
    }, []);

    const fetchMesDemandes = async () => {
        setLoading(true);
        try {
            const data: ContratLocataire[] = await authenticatedFetch('locataire/mes-demandes-contrats', { method: 'GET' });
            setMesDemandes(data);
            toast.success("Vos demandes et contrats ont été chargés.");
        } catch (error: any) {
            console.error('Erreur lors du chargement de vos demandes et contrats:', error);
            toast.error("Échec du chargement.", { description: error.message || "Erreur inconnue." });
        } finally {
            setLoading(false);
        }
    };

    const getStatusBadgeVariant = (status: string) => {
        switch (status) {
            case 'en_attente_validation': return 'secondary'; // Utilisez une variante 'warning' si vous l'avez
            case 'actif': return 'default';
            case 'rejete': return 'destructive';
            case 'termine': return 'secondary';
            default: return 'outline';
        }
    };

    if (loading) {
        return <div className="text-center p-8">Chargement de vos demandes et contrats...</div>;
    }

    return (
        <div className="container mx-auto p-4">
            <h1 className="text-3xl font-bold mb-6 text-center">Mes Demandes et Contrats de Location</h1>

            {mesDemandes.length === 0 ? (
                <div className="text-center p-8 text-gray-600 border rounded-lg">
                    <p className="text-lg">Vous n'avez pas encore de demandes ou de contrats de location.</p>
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
                            {/* <TableHead className="text-right">Détails</TableHead> */}
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {mesDemandes.map((contrat) => (
                            <TableRow key={contrat.id}>
                                <TableCell className="font-medium">{contrat.chambre_titre}</TableCell>
                                <TableCell>{contrat.proprietaire_nom || 'N/A'}</TableCell>
                                <TableCell>{format(new Date(contrat.date_debut), 'dd/MM/yyyy')}</TableCell>
                                <TableCell>{contrat.duree_mois} mois</TableCell>
                                <TableCell>{contrat.montant_caution.toLocaleString()} FCFA</TableCell>
                                <TableCell>
                                    <Badge variant={getStatusBadgeVariant(contrat.statut)} className={`
                                        ${contrat.statut === 'en_attente_validation' ? 'bg-yellow-100 text-yellow-800' : ''}
                                        ${contrat.statut === 'actif' ? 'bg-green-100 text-green-800' : ''}
                                        ${contrat.statut === 'rejete' ? 'bg-red-100 text-red-800' : ''}
                                        ${contrat.statut === 'termine' ? 'bg-gray-100 text-gray-800' : ''}
                                    `}>
                                        {contrat.statut.replace(/_/g, ' ')}
                                    </Badge>
                                </TableCell>
                                {/* <TableCell className="text-right">
                                    <Button variant="ghost" size="sm">Voir</Button>
                                </TableCell> */}
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            )}
        </div>
    );
};

export default LodgerMyRequestsPage;