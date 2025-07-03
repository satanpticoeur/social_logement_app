import React, { useState, useEffect } from 'react';
import type {Utilisateur} from '../types/common';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { toast } from 'sonner';
import { useAuth } from '@/context/AuthContext';
import { authenticatedFetch } from '@/lib/api';

const ClientsPage: React.FC = () => {
    const [clients, setClients] = useState<Utilisateur[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const { user } = useAuth(); // On utilise user pour un affichage conditionnel si nécessaire, mais plus le token

    useEffect(() => {
        const fetchClients = async () => {
            try {
                // Pas besoin de passer le token ici, le navigateur le fera via le cookie
                const data: Utilisateur[] = await authenticatedFetch('/locataires');
                setClients(data);
            } catch (err: any) {
                console.error("Erreur lors de la récupération des clients:", err);
                setError("Erreur lors du chargement des clients: " + err.message);
                toast.error("Erreur de chargement", {
                    description: err.message || "Impossible de récupérer la liste des clients.",
                });
            } finally {
                setLoading(false);
            }
        };

        // On vérifie que l'utilisateur est bien connecté (le user object est peuplé)
        // avant de tenter de fetch les clients, car cette route est protégée par PrivateRoute
        if (user) {
            fetchClients();
        } else {
            // Si user est null (non authentifié), PrivateRoute aurait déjà redirigé.
            // Ce else-block ne devrait pas être atteint en pratique si PrivateRoute fonctionne.
            setLoading(false);
            setError("Non authentifié.");
        }
    }, [user]); // Déclenche le useEffect quand l'objet user change (connexion/déconnexion)

    if (loading) {
        return <div className="text-center mt-10 text-muted-foreground">Chargement des clients...</div>;
    }

    if (error) {
        return <div className="text-destructive text-center mt-10">Erreur : {error}</div>;
    }

    return (
        <div className="p-4 bg-background text-foreground max-w-4xl mx-auto">
            <Card className="shadow-lg border-border">
                <CardHeader>
                    <CardTitle className="text-3xl font-bold text-primary">Liste de mes Clients</CardTitle>
                </CardHeader>
                <CardContent>
                    {clients.length > 0 ? (
                        <Table className="bg-card rounded-lg shadow-sm border border-border">
                            <TableHeader>
                                <TableRow>
                                    <TableHead>ID</TableHead>
                                    <TableHead>Nom d'utilisateur</TableHead>
                                    <TableHead>Email</TableHead>
                                    <TableHead>Téléphone</TableHead>
                                    <TableHead>CNI</TableHead>
                                    <TableHead>Créé le</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {clients.map(client => (
                                    <TableRow key={client.id}>
                                        <TableCell className="font-medium">{client.id}</TableCell>
                                        <TableCell>{client.nom_utilisateur}</TableCell>
                                        <TableCell>{client.email}</TableCell>
                                        <TableCell>{client.telephone}</TableCell>
                                        <TableCell>{client.cni}</TableCell>
                                        <TableCell>{new Date(client.cree_le).toLocaleDateString()}</TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    ) : (
                        <p className="text-center text-muted-foreground mt-4">Aucun client trouvé.</p>
                    )}
                </CardContent>
            </Card>
        </div>
    );
};

export default ClientsPage;