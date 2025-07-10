import React, {useEffect, useState} from 'react';
import {useNavigate} from 'react-router-dom';
import {authenticatedFetch} from '@/lib/api.ts';
import {toast} from 'sonner';
import {useAuth} from "@/context/AuthContext.tsx";

interface Paiement {
    id: number;
    montant: number;
    date_paiement: string; // ISO string
    est_paye: boolean;
    periode_couverte_debut: string | null;
    periode_couverte_fin: string | null;
    chambre_nom: string;
    locataire_email: string;
}

interface PaiementsResponse {
    paiements: Paiement[];
    dashboard_summary: {
        total_paye: number;
        total_impaye: number;
        nombre_paiements_payes: number;
        nombre_paiements_impayes: number;
    };
}

const OwnerPaymentsPage: React.FC = () => {
    const {user, isAuthenticated} = useAuth();
    const navigate = useNavigate();
    const [paiements, setPaiements] = useState<Paiement[]>([]);
    const [summary, setSummary] = useState<PaiementsResponse["dashboard_summary"]>(); // Pour le petit dashboard
    const [loading, setLoading] = useState<boolean>(true);

    useEffect(() => {
        if (!isAuthenticated || user?.role !== 'proprietaire') {
            toast.error("Accès refusé. Veuillez vous connecter en tant que propriétaire.");
            navigate('/login');
            return;
        }
        fetchPaiements();
    }, [isAuthenticated, user, navigate]);

    const fetchPaiements = async () => {
        try {
            setLoading(true);
            const data: PaiementsResponse = await authenticatedFetch('/proprietaire/paiements', {method: 'GET'});
            setPaiements(data.paiements);
            setSummary(data.dashboard_summary);
            toast.success("Liste des paiements chargée.");
        } catch (error: any) {
            console.error('Erreur lors du chargement des paiements:', error);
            toast.error("Échec du chargement des paiements.", {description: error.message || "Erreur inconnue."});
        } finally {
            setLoading(false);
        }
    };

    const getPaiementStatusClass = (estPaye: boolean) => {
        return estPaye ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800';
    };

    if (loading) {
        return <p>Chargement des paiements...</p>;
    }

    return (
        <div className="container mx-auto p-4">
            <h2 className="text-2xl font-bold mb-4">Mes Paiements</h2>

            {summary && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                    <div className="bg-blue-100 p-4 rounded-lg shadow">
                        <h3 className="font-semibold">Total Payé</h3>
                        <p className="text-xl font-bold">{summary.total_paye.toFixed(2)} FCFA</p>
                        <p className="text-sm text-gray-600">({summary.nombre_paiements_payes} paiements)</p>
                    </div>
                    <div className="bg-red-100 p-4 rounded-lg shadow">
                        <h3 className="font-semibold">Total Impayé</h3>
                        <p className="text-xl font-bold">{summary.total_impaye.toFixed(2)} FCFA</p>
                        <p className="text-sm text-gray-600">({summary.nombre_paiements_impayes} paiements)</p>
                    </div>
                </div>
            )}

            {paiements.length === 0 ? (
                <p>Aucun paiement trouvé pour le moment.</p>
            ) : (
                <div className="overflow-x-auto">
                    <table className="min-w-full bg-white shadow-md rounded-lg overflow-hidden">
                        <thead className="bg-gray-200 text-gray-700">
                        <tr>
                            <th className="py-2 px-4 text-left">Chambre</th>
                            <th className="py-2 px-4 text-left">Locataire</th>
                            <th className="py-2 px-4 text-left">Montant</th>
                            <th className="py-2 px-4 text-left">Date Paiement</th>
                            <th className="py-2 px-4 text-left">Période Couverte</th>
                            <th className="py-2 px-4 text-left">Statut</th>
                        </tr>
                        </thead>
                        <tbody>
                        {paiements.map(paiement => (
                            <tr key={paiement.id} className="border-b border-gray-200 hover:bg-gray-50">
                                <td className="py-2 px-4">{paiement.chambre_nom}</td>
                                <td className="py-2 px-4">{paiement.locataire_email}</td>
                                <td className="py-2 px-4">{paiement.montant.toFixed(2)} FCFA</td>
                                <td className="py-2 px-4">{new Date(paiement.date_paiement).toLocaleDateString()}</td>
                                <td className="py-2 px-4">
                                    {paiement.periode_couverte_debut && paiement.periode_couverte_fin
                                        ? `${new Date(paiement.periode_couverte_debut).toLocaleDateString()} - ${new Date(paiement.periode_couverte_fin).toLocaleDateString()}`
                                        : 'N/A'}
                                </td>
                                <td className="py-2 px-4">
                    <span
                        className={`px-2 py-1 rounded-full text-xs font-semibold ${getPaiementStatusClass(paiement.est_paye)}`}>
                      {paiement.est_paye ? 'Payé' : 'Impayé'}
                    </span>
                                </td>
                            </tr>
                        ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
};

export default OwnerPaymentsPage;