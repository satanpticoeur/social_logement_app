import React, {useState, useEffect} from 'react';
import type {Chambre} from '../types/common';
import {Link} from 'react-router-dom';
import {Button} from '@/components/ui/button';

export const RoomListPage: React.FC = () => {
    const [chambres, setChambres] = useState<Chambre[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

    useEffect(() => {
        fetch(`${BACKEND_URL}/api/chambres`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Erreur HTTP: ${response.status}`);
                }
                return response.json();
            })
            .then((data: Chambre[]) => {
                setChambres(data);
                setLoading(false);
            })
            .catch((err: Error) => {
                console.error("Erreur lors de la récupération des chambres:", err);
                setError("Erreur lors du chargement des chambres: " + err.message);
                setLoading(false);
            });
    }, [BACKEND_URL]);

    if (error) {
        return <div className="text-destructive text-center mt-10">Erreur : {error}</div>;
    }

    return (
        <div className="p-4 bg-background text-foreground">
            <h1 className="text-3xl font-bold mb-6 text-center text-foreground">Nos Chambres Disponibles</h1>

            {loading ? (
                <p className="text-center text-muted-foreground">Chargement des chambres...</p>
            ) : chambres.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
                    {chambres.map(chambre => (
                        <div key={chambre.id}
                             className="bg-card rounded-lg shadow-md hover:shadow-xl transition-shadow duration-300 overflow-hidden border border-border"> {/* Utilise bg-card et border-border */}
                            {/* Affichage de la première image si disponible */}
                            {chambre.medias && chambre.medias.length > 0 && (
                                <img
                                    src={chambre.medias[0].url}
                                    alt={chambre.titre}
                                    className="w-full h-48 object-cover"
                                />
                            )}
                            <div className="p-5">
                                <h2 className="text-xl font-semibold mb-2 text-foreground">{chambre.titre}</h2>
                                <p className="text-muted-foreground mb-1"> {/* Utilise text-muted-foreground */}
                                    <span className="font-medium">Prix :</span> {chambre.prix} XOF
                                    / {chambre.type === 'simple' ? 'mois' : 'mois'}
                                </p>
                                <p className="text-muted-foreground mb-1">
                                    <span className="font-medium">Taille :</span> {chambre.taille}
                                </p>
                                {chambre.maison && (
                                    <p className="text-muted-foreground mb-3">
                                        <span className="font-medium">Adresse :</span> {chambre.maison.adresse}
                                    </p>
                                )}
                                <div
                                    className="flex items-center space-x-2 text-sm text-muted-foreground mb-3"> {/* Utilise text-muted-foreground */}
                                    {chambre.meublee ? (
                                        <span
                                            className="inline-flex items-center rounded-md bg-accent px-2 py-1 text-xs font-medium text-accent-foreground ring-1 ring-inset ring-accent">Meublée</span>
                                    ) : (
                                        <span
                                            className="inline-flex items-center rounded-md bg-destructive/10 px-2 py-1 text-xs font-medium text-destructive ring-1 ring-inset ring-destructive">Non Meublée</span>
                                    )}
                                    {chambre.salle_de_bain && (
                                        <span
                                            className="inline-flex items-center rounded-md bg-secondary px-2 py-1 text-xs font-medium text-secondary-foreground ring-1 ring-inset ring-secondary">SDB</span>
                                        )}
                                    <span
                                        className="inline-flex items-center rounded-md bg-primary/10 px-2 py-1 text-xs font-medium text-primary ring-1 ring-inset ring-primary">
                                        {chambre.type}
                    </span>
                                </div>

                                <Link to={`/chambres/${chambre.id}`}>
                                    <Button className="w-full mt-4">Voir les détails</Button>
                                </Link>
                            </div>
                        </div>
                    ))}
                </div>
            ) : (
                <p className="text-center text-muted-foreground">Aucune chambre trouvée pour le moment.</p>
            )}
        </div>
    );
};

