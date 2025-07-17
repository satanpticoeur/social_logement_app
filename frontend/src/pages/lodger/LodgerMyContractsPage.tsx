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
    statut: string; // 'actif', 'rejete', 'termine', 'resilie'
}

const LodgerMyContractsPage: React.FC = () => { // Renommé ici
    const [mesContrats, setMesContrats] = useState<ContratLocataire[]>([]); // Renommé ici
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchMesContrats(); // Appel renommé
    }, []);

    const fetchMesContrats = async () => { // Fonction renommée
        setLoading(true);
        try {
            // L'endpoint backend existant, mais sera modifié pour exclure 'en_attente_validation'
            const data: ContratLocataire[] = await authenticatedFetch('locataire/mes-contrats', { method: 'GET' }); // Nouvelle route backend
            setMesContrats(data);
            toast.success("Vos contrats ont été chargés.");
        } catch (error: any) {
            console.error('Erreur lors du chargement de vos contrats:', error);
            toast.error("Échec du chargement.", { description: error.message || "Erreur inconnue." });
        } finally {
            setLoading(false);
        }
    };

    const getStatusBadgeVariant = (status: string) => {
        switch (status) {
            case 'actif': return 'default';
            case 'rejete': return 'destructive';
            case 'termine': return 'secondary';
            case 'resilie': return 'destructive'; // Si vous introduisez ce statut côté locataire
            default: return 'outline';
        }
    };

    if (loading) {
        return <div className="text-center p-8">Chargement de vos contrats...</div>;
    }

    return (
        <div className="container mx-auto p-4">
            <h1 className="text-3xl font-bold mb-6 text-center">Mes Contrats de Location</h1> {/* Titre adapté */}

            {mesContrats.length === 0 ? (
                <div className="text-center p-8 text-muted-foreground border rounded-lg">
                    <p className="text-lg">Vous n'avez pas encore de contrats actifs, rejetés ou terminés.</p>
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
                        {mesContrats.map((contrat) => (
                            <TableRow key={contrat.id}>
                                <TableCell className="font-medium">{contrat.chambre_titre}</TableCell>
                                <TableCell>{contrat.proprietaire_nom || 'N/A'}</TableCell>
                                <TableCell>{format(new Date(contrat.date_debut), 'dd/MM/yyyy')}</TableCell>
                                <TableCell>{contrat.duree_mois} mois</TableCell>
                                <TableCell>{contrat.montant_caution.toLocaleString()} FCFA</TableCell>
                                <TableCell>
                                    <Badge variant={getStatusBadgeVariant(contrat.statut)} className={`
                                        ${contrat.statut === 'actif' ? 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100' : ''}
                                        ${contrat.statut === 'rejete' ? 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-100' : ''}
                                        ${contrat.statut === 'termine' ? 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-100' : ''}
                                        ${contrat.statut === 'resilie' ? 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-100' : ''}
                                    `}>
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

export default LodgerMyContractsPage;