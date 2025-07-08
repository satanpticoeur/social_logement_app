import React, {useEffect, useState} from 'react';
import {useNavigate} from 'react-router-dom';
import {authenticatedFetch} from '@/lib/api.ts';
import {toast} from 'sonner';
import {Card, CardContent, CardHeader, CardTitle} from "@/components/ui/card.tsx";
import {useAuth} from "@/context/UseAuth.tsx";

interface Client {
    cni: string
    email: string
    id: number
    nom_utilisateur: string
    telephone: string
}

const OwnerClientsPage: React.FC = () => {
    const {user, isAuthenticated} = useAuth();
    const navigate = useNavigate();
    const [clients, setClients] = useState<Client[]>([]);
    const [loading, setLoading] = useState<boolean>(true);

    useEffect(() => {
        if (!isAuthenticated || user?.role !== 'proprietaire') {
            toast.error("Accès refusé. Veuillez vous connecter en tant que propriétaire.");
            navigate('/login');
            return;
        }
        fetchClients();
    }, [isAuthenticated, user, navigate]);

    const fetchClients = async () => {
        try {
            setLoading(true);
            const data = await authenticatedFetch('proprietaire/clients', {method: 'GET'});
            setClients(data);
            console.log(data)
            toast.success("Liste des clients chargée.");
        } catch (error: any) {
            console.error('Erreur lors du chargement des clients:', error);
            toast.error("Échec du chargement des clients.", {description: error.message || "Erreur inconnue."});
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return <p>Chargement des clients...</p>;
    }

    return (
        <div className="container mx-auto p-4">
            <h2 className="text-2xl font-bold mb-4">Mes Clients (Locataires)</h2>
            {clients.length === 0 ? (
                <p>Aucun client trouvé pour le moment.</p>
            ) : (
                <div className="space-y-4">
                    {clients.map(client => (
                        //     on utilise les card de shadcn
                        <Card>
                            <CardHeader>
                                <CardTitle>{client.nom_utilisateur}</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <p>Email: {client.email}</p>
                                <p>Téléphone: {client.telephone}</p>
                                <p>CNI: {client.cni}</p>
                            </CardContent>
                        </Card>
                    ))}
                </div>
            )}
        </div>
    );
};

export default OwnerClientsPage;