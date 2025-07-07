import React, {useState, useEffect} from 'react';
import type {Utilisateur} from '../../types/common.ts'; // Assure-toi que le chemin est correct

export const UserListPage: React.FC = () => {
    const [utilisateurs, setUtilisateurs] = useState<Utilisateur[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

    useEffect(() => {
        fetch(`${BACKEND_URL}/api/utilisateurs`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Erreur HTTP: ${response.status}`);
                }
                return response.json();
            })
            .then((data: Utilisateur[]) => {
                setUtilisateurs(data);
                setLoading(false);
            })
            .catch((err: Error) => {
                console.error("Erreur lors de la récupération des utilisateurs:", err);
                setError("Erreur lors du chargement des utilisateurs: " + err.message);
                setLoading(false);
            });
    }, [BACKEND_URL]); // Ajoute BACKEND_URL aux dépendances de useEffect

    if (error) {
        return <div className="text-red-500 text-center mt-10">Erreur : {error}</div>;
    }

    return (
        <div className="p-4 bg-background text-foreground"> {/* Utilise bg-background et text-foreground */}
            <h1 className="text-3xl font-bold mb-6 text-center text-foreground">Liste des Utilisateurs</h1>

            {loading ? (
                <p className="text-center text-muted-foreground">Chargement des utilisateurs...</p>
            ) : utilisateurs.length > 0 ? (
                <ul className="space-y-4 max-w-2xl mx-auto">
                    {utilisateurs.map(user => (
                        <li key={user.id}
                            className="bg-card p-4 rounded-lg shadow flex justify-between items-center border border-border">
                            <div>
                                <p className="font-semibold text-lg text-foreground">{user.nom_utilisateur}</p>
                                <p className="text-sm text-muted-foreground">{user.email} - {user.role}</p>
                                {user.telephone &&
                                    <p className="text-sm text-muted-foreground">Tél: {user.telephone}</p>}
                            </div>
                        </li>
                    ))}
                </ul>
            ) : (
                <p className="text-center text-muted-foreground">Aucun utilisateur trouvé.</p>
            )}
        </div>
    );
};

