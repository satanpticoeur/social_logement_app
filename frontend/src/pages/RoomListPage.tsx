import React, { useState, useEffect } from 'react';
import type {Chambre} from '../types/common';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';

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
        return <div className="text-red-500 text-center mt-10">Erreur : {error}</div>;
    }

    return (
        <div className="p-4">
            <h1 className="text-3xl font-bold mb-6 text-center text-gray-900 dark:text-white">Nos Chambres Disponibles</h1>

            {loading ? (
                <p className="text-center text-gray-600 dark:text-gray-300">Chargement des chambres...</p>
            ) : chambres.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
                    {chambres.map(chambre => (
                        <div key={chambre.id} className="bg-white dark:bg-gray-800 rounded-lg shadow-md hover:shadow-xl transition-shadow duration-300 overflow-hidden">
                            {/* Affichage de la première image si disponible */}
                            {chambre.medias && chambre.medias.length > 0 && (
                                <img
                                    src={chambre.medias[0].url}
                                    alt={chambre.titre}
                                    className="w-full h-48 object-cover"
                                />
                            )}
                            <div className="p-5">
                                <h2 className="text-xl font-semibold mb-2 text-gray-900 dark:text-white">{chambre.titre}</h2>
                                <p className="text-gray-700 dark:text-gray-300 mb-1">
                                    <span className="font-medium">Prix :</span> {chambre.prix} XOF / {chambre.type === 'simple' ? 'mois' : 'mois'} {/* Ajuste la période si nécessaire */}
                                </p>
                                <p className="text-gray-700 dark:text-gray-300 mb-1">
                                    <span className="font-medium">Taille :</span> {chambre.taille}
                                </p>
                                {chambre.maison && (
                                    <p className="text-gray-700 dark:text-gray-300 mb-3">
                                        <span className="font-medium">Adresse :</span> {chambre.maison.adresse}
                                    </p>
                                )}
                                <div className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400 mb-3">
                                    {chambre.meublee ? (
                                        <span className="inline-flex items-center rounded-md bg-green-50 px-2 py-1 text-xs font-medium text-green-700 ring-1 ring-inset ring-green-600/20">Meublée</span>
                                    ) : (
                                        <span className="inline-flex items-center rounded-md bg-red-50 px-2 py-1 text-xs font-medium text-red-700 ring-1 ring-inset ring-red-600/20">Non Meublée</span>
                                    )}
                                    {chambre.salle_de_bain && (
                                        <span className="inline-flex items-center rounded-md bg-blue-50 px-2 py-1 text-xs font-medium text-blue-700 ring-1 ring-inset ring-blue-600/20">SDB</span>
                                    )}
                                    <span className="inline-flex items-center rounded-md bg-purple-50 px-2 py-1 text-xs font-medium text-purple-700 ring-1 ring-inset ring-purple-600/20">{chambre.type}</span>
                                </div>

                                <Link to={`/chambres/${chambre.id}`}>
                                    <Button className="w-full mt-4 bg-blue-600 hover:bg-blue-700">Voir les détails</Button>
                                </Link>
                            </div>
                        </div>
                    ))}
                </div>
            ) : (
                <p className="text-center text-gray-500 dark:text-gray-400">Aucune chambre trouvée pour le moment.</p>
            )}
        </div>
    );
};

