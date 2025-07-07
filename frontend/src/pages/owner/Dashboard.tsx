
import {useEffect, useState} from 'react';
import {useAuth} from '../../context/AuthContext';
import {useNavigate} from 'react-router-dom';
import {authenticatedFetch} from '@/lib/api.ts'; // Votre fonction fetch authentifiée
import {toast} from 'sonner';

interface DashboardSummary {
    total_paye: number;
    total_impaye: number;
    nombre_paiements_payes: number;
    nombre_paiements_impayes: number;
}

export default function Page() {
    const {user, isAuthenticated} = useAuth();
    const navigate = useNavigate();
    const [summary, setSummary] = useState<DashboardSummary | null>(null);
    const [loading, setLoading] = useState<boolean>(true);



    useEffect(() => {
        if (!isAuthenticated || user?.role !== 'proprietaire') {
            toast.error("Accès refusé. Veuillez vous connecter en tant que propriétaire.");
            navigate('/login');
            return;
        }
        fetchDashboardSummary();
    }, [isAuthenticated, user, navigate]);

    const fetchDashboardSummary = async () => {
        try {
            setLoading(true);
            const data = await authenticatedFetch('proprietaire/paiements', {method: 'GET'});
            setSummary(data.dashboard_summary);
            toast.success("Résumé du tableau de bord chargé.");
        } catch (error: any) {
            console.error('Erreur lors du chargement du résumé:', error);
            toast.error("Échec du chargement du résumé.", {description: error.message || "Erreur inconnue."});
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return <p>Chargement du tableau de bord...</p>;
    }

    if (!summary) {
        return <p>Impossible de charger les données du tableau de bord.</p>;
    }

    return (
        <div className="flex flex-1 flex-col gap-4 p-4">
            <div className="grid auto-rows-min gap-4 md:grid-cols-2">
                <div className="p-4 bg-muted/50 aspect-video rounded-xl">
                    <p className="font-semibold">Total Payé :
                    </p>
                    <p>
                        {
                            summary.total_paye
                        }
                        <span> fcfa </span>
                        {
                            summary.nombre_paiements_payes
                        }
                        <span> paiemnts</span>
                    </p>

                </div>
                <div className="p-4 bg-muted/50 aspect-video rounded-xl">
                    <p className="font-semibold">Total Impayé:
                    </p>
                    <p>
                        {
                            summary.total_impaye
                        }
                        <span> fcfa </span>
                        {
                            summary.nombre_paiements_impayes
                        }
                        <span> paiemnts</span>
                    </p>
                </div>
            </div>
            <div className="bg-muted/50 min-h-[100vh] flex-1 rounded-xl md:min-h-min">
                <div className="p-4">
                    <h2 className="text-2xl font-bold mb-4">Bienvenue dans votre tableau de
                        bord, {user?.email}!
                    </h2>
                </div>
            </div>
        </div>
    )
}
