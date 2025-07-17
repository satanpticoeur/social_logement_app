import React, { useEffect, useState } from 'react';
import { authenticatedFetch } from '@/lib/api.ts';
import { toast } from 'sonner';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button"; // Si vous voulez ajouter une action par chambre (ex: voir détails)
import { Link } from 'react-router-dom'; // Pour lier vers la page de détails de la chambre

// Interfaces (doivent correspondre aux données du backend)
interface MaisonData {
    id: number;
    nom: string;
    adresse: string;
    ville: string;
    description: string;
    proprietaire_id: number;
}

interface ChambreData {
    id: number;
    titre: string;
    description: string;
    prix: number;
    capacite: number;
    disponible: boolean;
    cree_le: string;
    mise_a_jour_le: string;
    maison: MaisonData | null;
}

const LodgerMyRoomsPage: React.FC = () => {
    const [mesChambres, setMesChambres] = useState<ChambreData[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchMesChambres();
    }, []);

    const fetchMesChambres = async () => {
        setLoading(true);
        try {
            const data: ChambreData[] = await authenticatedFetch('locataire/mes-chambres', { method: 'GET' });
            setMesChambres(data);
            console.log(data)
            toast.success(`${data.length} chambres associées chargées.`);
        } catch (error: any) {
            console.error('Erreur lors du chargement de vos chambres associées:', error);
            toast.error("Échec du chargement des chambres.", { description: error.message || "Erreur inconnue." });
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return <div className="text-center p-8">Chargement de vos chambres associées...</div>;
    }

    return (
        <div className="container mx-auto p-4">
            <h1 className="text-3xl font-bold mb-6 text-center">Mes Chambres Associées</h1>

            {mesChambres.length === 0 ? (
                <div className="text-center p-8 text-gray-600 border rounded-lg">
                    <p className="text-lg">Vous n'avez pas encore de chambres associées à vos contrats.</p>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {mesChambres.map((chambre) => (
                        <Card key={chambre.id} className="flex flex-col">
                            <CardHeader>
                                <CardTitle>{chambre.titre}</CardTitle>
                                {chambre.maison && (
                                    <CardDescription>
                                        {chambre.maison.adresse}, {chambre.maison.ville}
                                    </CardDescription>
                                )}
                            </CardHeader>
                            <CardContent className="flex-grow">
                                <p className="mb-2"><strong>Prix Mensuel:</strong> {chambre.prix.toLocaleString()} FCFA</p>
                                <p className="mb-2"><strong>Capacité:</strong> {chambre.capacite} personnes</p>
                                <p className="mb-2">
                                    <strong>Statut:</strong>{' '}
                                    <Badge variant={chambre.disponible ? 'default' : 'secondary'}>
                                        {chambre.disponible ? 'Disponible' : 'Occupée'}
                                    </Badge>
                                </p>
                                {chambre.description && (
                                    <p className="mt-3 text-sm text-gray-600">
                                        <strong>Description:</strong> "{chambre.description.substring(0, 100)}{chambre.description.length > 100 ? '...' : ''}"
                                    </p>
                                )}
                            </CardContent>
                            <CardFooter className="flex justify-end">
                                <Link to={`${chambre.id}`}>
                                    <Button variant="outline" size="sm">Voir les détails</Button>
                                </Link>
                            </CardFooter>
                        </Card>
                    ))}
                </div>
            )}
        </div>
    );
};

export default LodgerMyRoomsPage;