
import { useState, useEffect } from 'react';
import type {Utilisateur} from './types/common';

function App() {
    const [error, setError] = useState<string | null>(null);
    const [utilisateurs, setUtilisateurs] = useState<Utilisateur[]>([]);
    const [loading, setLoading] = useState<boolean>(true);

    const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

    useEffect(() => {
        // Récupération de la liste des utilisateurs
        fetch(`${BACKEND_URL}/api/utilisateurs`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Erreur HTTP: ${response.status}`);
                }
                return response.json();
            })
            .then((data: Utilisateur[]) => { // Ici on s'attend à un tableau d'Utilisateur
                setUtilisateurs(data);
                setLoading(false);
            })
            .catch((err: Error) => {
                console.error("Erreur lors de la récupération des utilisateurs:", err);
                setError(prev => (prev ? prev + "; Erreur utilisateurs: " + err.message : "Erreur utilisateurs: " + err.message));
                setLoading(false);
            });

    }, [BACKEND_URL]);

    if (error) {
        return <div className="App"><h1>Erreur</h1><p>{error}</p></div>;
    }

    return (
        <div className="App">
            <header className="App-header">
                <h1>Frontend Social Logement App</h1>
                <h2>Liste des Utilisateurs</h2>
                {loading ? (
                    <p>Chargement des utilisateurs...</p>
                ) : utilisateurs.length > 0 ? (
                    <ul>
                        {utilisateurs.map(user => (
                            <li key={user.id}>
                                {user.nom_utilisateur} ({user.email}) - {user.role}
                            </li>
                        ))}
                    </ul>
                ) : (
                    <p>Aucun utilisateur trouvé.</p>
                )}
            </header>
        </div>
    );
}

export default App;