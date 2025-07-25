import React, {useEffect, useState} from 'react';
import {authenticatedFetch} from '@/lib/api.ts';
import {toast} from 'sonner';
import {Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle} from "@/components/ui/card.tsx";
import {Badge} from "@/components/ui/badge.tsx";
import {Button} from "@/components/ui/button.tsx";
import {Link} from 'react-router-dom';

interface ContratLocataire {
    id: number;
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
    statut: string; // 'actif', 'resilié', etc.
    description: string | null;
    cree_le: string;
}

const LodgerContractsPage: React.FC = () => {
    const [contrats, setContrats] = useState<ContratLocataire[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        console.log("Chargement des contrats de location...");
        fetchContrats();
    }, []);

    const fetchContrats = async () => {
        setLoading(true);
        try {
            const data: ContratLocataire[] = await authenticatedFetch('locataire/contrats', {method: 'GET'});
            setContrats(data);
            toast.success(`${data.length} contrats chargés.`);
        } catch (error: any) {
            console.error('Erreur lors du chargement des contrats:', error);
            toast.error("Échec du chargement des contrats.", {description: error.message || "Erreur inconnue."});
        } finally {
            setLoading(false);
        }
    };

    const getStatusBadgeVariant = (status: string) => {
        switch (status) {
            case 'actif':
                return 'default';
            case 'resilié':
                return 'destructive';
            default:
                return 'secondary';
        }
    };

    if (loading) {
        return <div className="text-center p-4">Chargement de vos contrats...</div>;
    }

    return (
        <div className="container mx-auto p-4">
            <h1 className="text-3xl font-bold mb-6 text-center">Mes Contrats de Location</h1>

            {contrats.length === 0 ? (
                <p className="text-center text-lg text-gray-600">Vous n'avez aucun contrat de location pour le
                    moment.</p>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {contrats.map((contrat) => (
                        <Card key={contrat.id} className="flex flex-col">
                            {/* ... (CardHeader et CardContent existants) ... */}
                            <CardHeader>
                                <CardTitle>{contrat.chambre_titre}</CardTitle>
                                <CardDescription>{contrat.chambre_adresse}</CardDescription>
                            </CardHeader>
                            <CardContent className="flex-grow">
                                <p className="mb-2"><strong>Statut:</strong> <Badge
                                    variant={getStatusBadgeVariant(contrat.statut)}
                                    className="ml-2">{contrat.statut.replace('_', ' ')}</Badge></p>
                                <p className="mb-1">
                                    <strong>Début:</strong> {new Date(contrat.date_debut).toLocaleDateString('fr-FR')}
                                </p>
                                <p className="mb-1">
                                    <strong>Fin:</strong> {new Date(contrat.date_fin).toLocaleDateString('fr-FR')}</p>
                                <p className="mb-1"><strong>Loyer
                                    Mensuel:</strong> {contrat.prix_mensuel_chambre.toLocaleString('fr-FR')} FCFA</p>
                                {contrat.montant_caution && (
                                    <p className="mb-1">
                                        <strong>Caution:</strong> {contrat.montant_caution.toLocaleString('fr-FR')} FCFA
                                        ({contrat.mois_caution} mois)</p>
                                )}
                                <p className="mb-1"><strong>Périodicité:</strong> {contrat.periodicite}</p>
                                <p className="mb-1"><strong>Mode de Paiement:</strong> {contrat.mode_paiement}</p>
                                {contrat.description && (
                                    <p className="mt-3 text-sm text-gray-600">
                                        <strong>Description:</strong> "{contrat.description}"</p>
                                )}
                            </CardContent>
                            <CardFooter className="flex justify-end gap-2">
                                {/* Nouveau bouton pour voir les paiements */}
                                <Link to={`/locataire/contrats/${contrat.id}/paiements`}>
                                    <Button variant="outline" size="sm">Voir les paiements</Button>
                                </Link>
                                <Link
                                    to={`/locataire/contrats/${contrat.id}`}> {/* Pour la gestion future du contrat */}
                                    <Button variant="outline" size="sm">Gérer</Button>
                                </Link>
                            </CardFooter>
                        </Card>
                    ))}
                </div>
            )}
        </div>
    );
};

export default LodgerContractsPage;