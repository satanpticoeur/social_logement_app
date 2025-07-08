// src/pages/LocatairePaiementsPage.tsx
import React, {useEffect, useState} from 'react';
import {useNavigate, useParams} from 'react-router-dom';
import {authenticatedFetch} from '@/lib/api.ts';
import {toast} from 'sonner';
import {Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle} from "@/components/ui/card.tsx";
import {Badge} from "@/components/ui/badge.tsx";
import {Button} from "@/components/ui/button.tsx";

interface Paiement {
    id: number;
    montant: number;
    date_echeance: string;
    date_paiement: string | null;
    statut: 'payé' | 'impayé' | 'partiel';
    description: string | null;
    cree_le: string;
}

const LodgerPaymentsPage: React.FC = () => {
    const {contratId} = useParams<{ contratId: string }>();
    const navigate = useNavigate();
    const [paiements, setPaiements] = useState<Paiement[]>([]);
    const [loading, setLoading] = useState(true);
    const [contratInfo, setContratInfo] = useState({chambreTitre: '', chambreAdresse: ''});


    useEffect(() => {
        if (contratId) {
            fetchPaiements();
            fetchContratInfo(Number(contratId)); // Récupérer des infos pour le titre
        }
    }, [contratId]);

    const fetchContratInfo = async (id: number) => {
        try {
            // Utiliser l'endpoint de détails de contrat pour récupérer les infos
            const data = await authenticatedFetch(`locataire/contrats/${id}`, {method: 'GET'});
            setContratInfo({
                chambreTitre: data.chambre_titre,
                chambreAdresse: data.chambre_adresse
            });
        } catch (error) {
            console.error("Erreur lors de la récupération des infos du contrat:", error);
            toast.error("Impossible de charger les informations du contrat.");
        }
    };


    const fetchPaiements = async () => {
        setLoading(true);
        try {
            // Pour l'instant, le locataire n'a pas d'endpoint direct /contrats/:id/paiements
            // Il faudrait soit l'ajouter au backend, soit récupérer tous les paiements du locataire
            // et filtrer (moins efficace).
            // Pour le MVP, on peut créer un endpoint temporaire ou supposer que l'endpoint
            // `/locataire/contrats/<int:contrat_id>` renverrait aussi les paiements.
            // OU: ajouter un endpoint dans locataire_routes.py:
            // @locataire_bp.route('/contrats/<int:contrat_id>/paiements', methods=['GET'])
            // qui serait similaire à celui du propriétaire.

            // Pour l'exemple, supposons que nous avons cet endpoint:
            const data: Paiement[] = await authenticatedFetch(`locataire/contrats/${contratId}/paiements`, {method: 'GET'});
            setPaiements(data);
            toast.success(`${data.length} paiements chargés.`);
        } catch (error: any) {
            console.error('Erreur lors du chargement des paiements:', error);
            toast.error("Échec du chargement des paiements.", {description: error.message || "Erreur inconnue."});
            // navigate('/locataire/contrats'); // Rediriger en cas d'erreur
        } finally {
            setLoading(false);
        }
    };

    const getStatusBadgeVariant = (status: string) => {
        switch (status) {
            case 'payé':
                return 'default';
            case 'impayé':
                return 'destructive';
            case 'partiel':
                return 'secondary';
            default:
                return 'outline';
        }
    };

    if (loading) {
        return <div className="text-center p-4">Chargement des paiements...</div>;
    }

    return (
        <div className="container mx-auto p-4">
            <Button onClick={() => navigate(-1)} className="mb-6">Retour aux contrats</Button>
            <h1 className="text-3xl font-bold mb-4 text-center">Échéancier de Paiements</h1>
            <h2 className="text-xl text-gray-700 mb-6 text-center">
                pour "{contratInfo.chambreTitre}" - {contratInfo.chambreAdresse}
            </h2>

            {paiements.length === 0 ? (
                <p className="text-center text-lg text-gray-600">Aucun paiement enregistré pour ce contrat.</p>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {paiements.map((paiement) => (
                        <Card key={paiement.id} className="flex flex-col">
                            <CardHeader>
                                <CardTitle>Montant: {paiement.montant.toLocaleString('fr-FR')} FCFA</CardTitle>
                                <CardDescription>Échéance: {new Date(paiement.date_echeance).toLocaleDateString('fr-FR')}</CardDescription>
                            </CardHeader>
                            <CardContent className="flex-grow">
                                <p className="mb-2"><strong>Statut:</strong> <Badge
                                    variant={getStatusBadgeVariant(paiement.statut)}
                                    className="ml-2">{paiement.statut}</Badge></p>
                                {paiement.date_paiement && (
                                    <p className="mb-1"><strong>Payé
                                        le:</strong> {new Date(paiement.date_paiement).toLocaleDateString('fr-FR')}</p>
                                )}
                                {paiement.description && (
                                    <p className="mt-2 text-sm text-gray-600">
                                        <strong>Description:</strong> "{paiement.description}"</p>
                                )}
                            </CardContent>
                            <CardFooter className="flex justify-end">
                                {/* Ici, un locataire n'aura pas de bouton "Marquer payé", mais potentiellement "Payer maintenant" */}
                                {paiement.statut === 'impayé' && (
                                    <Button disabled>Payer maintenant (à implémenter)</Button>
                                )}
                            </CardFooter>
                        </Card>
                    ))}
                </div>
            )}
        </div>
    );
};

export default LodgerPaymentsPage;