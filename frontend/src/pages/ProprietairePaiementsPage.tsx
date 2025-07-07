// src/pages/ProprietairePaiementsPage.tsx
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { authenticatedFetch } from '@/lib/api';
import { toast } from 'sonner';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

interface Paiement {
    id: number;
    montant: number;
    date_echeance: string;
    date_paiement: string | null;
    statut: 'payé' | 'impayé' | 'partiel';
    description: string | null;
    cree_le: string;
}

const ProprietairePaiementsPage: React.FC = () => {
    const { id } = useParams();
    const contratId = id || '';
    const navigate = useNavigate();
    const [paiements, setPaiements] = useState<Paiement[]>([]);
    const [loading, setLoading] = useState(true);
    const [contratInfo, setContratInfo] = useState({ chambreTitre: '', locataireNom: '' }); // Pour le titre de la page

    useEffect(() => {
        if (contratId) {
            fetchPaiements();
            // Optionnel: Récupérer des infos sur le contrat pour le titre de la page
            fetchContratDetailsForInfo(Number(contratId));
        }
    }, [contratId]);

    const fetchContratDetailsForInfo = async (id: number) => {
        try {
            // Endpoint à créer si vous n'avez pas de route PUT /proprietaire/contrats/<id>
            // Pour l'instant, on se base sur les infos disponibles dans le `get_proprietaire_contrats`
            // ou on pourrait créer un endpoint spécifique: `proprietaire/contrats/<id>`
            const data = await authenticatedFetch(`proprietaire/contrats`, { method: 'GET', credentials: "include" });
            const currentContrat = data.find((c: any) => c.id === id);
            if (currentContrat) {
                setContratInfo({
                    chambreTitre: currentContrat.chambre_titre,
                    locataireNom: currentContrat.locataire_nom_utilisateur
                });
            }
        } catch (error) {
            console.error("Erreur lors de la récupération des infos du contrat pour le titre:", error);
        }
    };

    const fetchPaiements = async () => {
        setLoading(true);
        try {
            const data: Paiement[] = await authenticatedFetch(`proprietaire/contrats/${contratId}/paiements`, { method: 'GET', credentials: "include" });
            setPaiements(data);
            console.log("Paiements chargés:", data);
            toast.success(`${data.length} paiements chargés.`);
        } catch (error: any) {
            console.error('Erreur lors du chargement des paiements:', error);
            toast.error("Échec du chargement des paiements.", { description: error.message || "Erreur inconnue." });
            // navigate('/proprietaire/contrats'); // Rediriger en cas d'erreur
        } finally {
            setLoading(false);
        }
    };

    const handleMarquerPaye = async (paiementId: number) => {
        if (!window.confirm("Êtes-vous sûr de vouloir marquer ce paiement comme 'payé' ?")) {
            return;
        }
        try {
            await authenticatedFetch(`proprietaire/paiements/${paiementId}/marquer_paye`, { method: 'PUT' });
            toast.success("Paiement marqué comme payé !");
            fetchPaiements(); // Recharger la liste pour mettre à jour le statut
        } catch (error: any) {
            console.error('Erreur lors du marquage du paiement:', error);
            toast.error("Échec du marquage du paiement.", { description: error.message || "Erreur inconnue." });
        }
    };

    const getStatusBadgeVariant = (status: string) => {
        switch (status) {
            case 'payé': return 'default';
            case 'impayé': return 'destructive';
            case 'partiel': return 'secondary';
            default: return 'outline';
        }
    };

    if (loading) {
        return <div className="text-center p-4">Chargement des paiements...</div>;
    }

    return (
        <div className="container mx-auto p-4">
            <Button onClick={() => navigate(-1)} className="mb-6">Retour aux contrats</Button>
            <h1 className="text-3xl font-bold mb-4 text-center">Gestion des Paiements</h1>
            <h2 className="text-xl text-gray-700 mb-6 text-center">
                pour "{contratInfo.chambreTitre}" - Locataire: {contratInfo.locataireNom}
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
                                <p className="mb-2"><strong>Statut:</strong> <Badge variant={getStatusBadgeVariant(paiement.statut)} className="ml-2">{paiement.statut}</Badge></p>
                                {paiement.date_paiement && (
                                    <p className="mb-1"><strong>Payé le:</strong> {new Date(paiement.date_paiement).toLocaleDateString('fr-FR')}</p>
                                )}
                                {paiement.description && (
                                    <p className="mt-2 text-sm text-gray-600"><strong>Description:</strong> "{paiement.description}"</p>
                                )}
                            </CardContent>
                            <CardFooter className="flex justify-end">
                                {paiement.statut === 'impayé' && (
                                    <Button
                                        onClick={() => handleMarquerPaye(paiement.id)}
                                        size="sm"
                                    >
                                        Marquer comme payé
                                    </Button>
                                )}
                            </CardFooter>
                        </Card>
                    ))}
                </div>
            )}
        </div>
    );
};

export default ProprietairePaiementsPage;