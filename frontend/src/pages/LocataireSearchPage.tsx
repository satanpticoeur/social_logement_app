import React, {useState, useEffect} from 'react';
import {authenticatedFetch} from '@/lib/api'; // Utilisez authenticatedFetch si la recherche nécessite une auth
import {toast} from 'sonner';
import {Button} from "@/components/ui/button";
import {Input} from "@/components/ui/input";
import {Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter} from "@/components/ui/card";
import {Badge} from "@/components/ui/badge";
import {Link} from 'react-router-dom'; // Pour naviguer vers les détails de la chambre
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from "@/components/ui/select";
import {Label} from '@/components/ui/label';
import {Slider} from "@/components/ui/slider.tsx";

// Interfaces (à s'assurer qu'elles sont cohérentes et importables si nécessaire)
interface Media {
    id: number;
    url: string;
    type: string | null;
    description: string | null;
}

interface Chambre {
    id: number;
    maison_id: number;
    adresse_maison: string;
    ville_maison: string;
    titre: string;
    description: string | null;
    taille: string | null;
    type: string | null;
    meublee: boolean;
    salle_de_bain: boolean;
    prix: number;
    disponible: boolean;
    cree_le: string;
    medias?: Media[];
}

const LocataireSearchPage: React.FC = () => {
    const [chambres, setChambres] = useState<Chambre[]>([]);
    const [loading, setLoading] = useState(false);
    const [searchParams, setSearchParams] = useState({
        ville: '',
        min_prix: '',
        max_prix: '',
        type: '',
        meublee: '', // 'true', 'false', ou '' pour tous
    });

    const [prixRange, setPrixRange] = useState<[number, number]>([0, 1000000]); // Exemple de range

    useEffect(() => {
        fetchChambres();
    }, []); // Dépendances vides pour un chargement au montage

    const fetchChambres = async () => {
        setLoading(true);
        try {
            // Construire la chaîne de requête (query string)
            const params = new URLSearchParams();
            if (searchParams.ville) params.append('ville', searchParams.ville);
            if (prixRange) params.append('min_prix', prixRange[0].toString());
            if (prixRange) params.append('max_prix', prixRange[1].toString());
            if (searchParams.type) params.append('type', searchParams.type);
            if (searchParams.meublee !== '') params.append('meublee', searchParams.meublee);
            params.append('disponible', 'true'); // Toujours filtrer par disponible pour le locataire

            const queryString = params.toString();
            const endpoint = `locataire/chambres/recherche${queryString ? `?${queryString}` : ''}`;

            const data: Chambre[] = await authenticatedFetch(endpoint, {
                method: 'GET',
                credentials: "include"
            });
            setChambres(data);
            toast.success(`${data.length} chambres trouvées.`);
        } catch (error: any) {
            console.error('Erreur lors de la recherche des chambres:', error);
            toast.error("Échec de la recherche de chambres.", {description: error.message || "Erreur inconnue."});
        } finally {
            setLoading(false);
        }
    };

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const {name, value} = e.target;
        setSearchParams(prev => ({...prev, [name]: value}));
    };

    const handleSelectChange = (name: string, value: string) => {
        setSearchParams(prev => ({...prev, [name]: value}));
    };

    const handleSearchSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        fetchChambres();
    };

    return (
        <div className="container mx-auto p-4">
            <h1 className="text-3xl font-bold mb-6 text-center">Trouvez Votre Chambre Idéale</h1>

            {/* Formulaire de Recherche et Filtres */}
            <form onSubmit={handleSearchSubmit}
                  className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4 mb-8 p-6 border rounded-lg shadow-sm bg-white">
                <div>
                    <Label htmlFor="ville">Ville</Label>
                    <Input id="ville" name="ville" value={searchParams.ville} onChange={handleInputChange}
                           placeholder="Dakar, Thiès..."/>
                </div>
                <div>
                    <Label htmlFor="type">Type de Chambre</Label>
                    <Select value={searchParams.type} onValueChange={(value) => handleSelectChange('type', value)}>
                        <SelectTrigger id="type">
                            <SelectValue placeholder="Sélectionner un type"/>
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="_">Tous les types</SelectItem>
                            <SelectItem value="simple">Simple</SelectItem>
                            <SelectItem value="double">Double</SelectItem>
                            <SelectItem value="studio">Studio</SelectItem>
                            <SelectItem value="appartement">Appartement</SelectItem>
                        </SelectContent>
                    </Select>
                </div>
                <div>
                    <Label htmlFor="meublee">Meublée</Label>
                    <Select value={searchParams.meublee}
                            onValueChange={(value) => handleSelectChange('meublee', value)}>
                        <SelectTrigger id="meublee">
                            <SelectValue placeholder="Oui/Non"/>
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="tous">Tous</SelectItem>
                            <SelectItem value="true">Oui</SelectItem>
                            <SelectItem value="false">Non</SelectItem>
                        </SelectContent>
                    </Select>
                </div>
                {/* Exemple d'intégration d'un Slider de prix si vous avez ce composant */}
                <div className="col-span-full">
                    <Label>Gamme de Prix</Label>
                    <Slider
                        min={0}
                        max={2000000} // Ajustez selon votre range de prix
                        step={10000}
                        value={prixRange}
                        onValueChange={(range) => setPrixRange(range as [number, number])}
                        className="mt-2"
                    />
                    <div className="text-sm text-gray-500 mt-1">
                        {prixRange[0].toLocaleString()} FCFA - {prixRange[1].toLocaleString()} FCFA
                    </div>
                </div>
                <Button type="submit" className="md:col-span-3 lg:col-span-4 mt-4" disabled={loading}>
                    {loading ? 'Recherche...' : 'Rechercher des Chambres'}
                </Button>
            </form>

            {/* Résultats de la Recherche */}
            {loading && <div className="text-center text-lg mt-8">Chargement des chambres...</div>}
            {!loading && chambres.length === 0 && (
                <div className="text-center text-lg mt-8 text-gray-600">
                    Aucune chambre ne correspond à vos critères de recherche.
                </div>
            )}
            {!loading && chambres.length > 0 && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {chambres.map((chambre) => (
                        <Card key={chambre.id}
                              className="flex flex-col h-full hover:shadow-lg transition-shadow duration-200">
                            <CardHeader className="p-0">
                                {chambre.medias && chambre.medias.length > 0 ? (
                                    <img
                                        src={chambre.medias[0].url}
                                        alt={chambre.titre}
                                        className="w-full h-56 object-cover rounded-t-lg"
                                    />
                                ) : (
                                    <div
                                        className="w-full h-56 bg-gray-200 flex items-center justify-center rounded-t-lg text-gray-500">
                                        Pas de photo disponible
                                    </div>
                                )}
                            </CardHeader>
                            <CardContent className="p-4 flex-grow">
                                <CardTitle className="text-xl font-semibold mb-2">{chambre.titre}</CardTitle>
                                <CardDescription className="text-gray-700 mb-2">
                                    {chambre.adresse_maison}, {chambre.ville_maison}
                                </CardDescription>
                                <div className="space-y-1 text-sm text-gray-800">
                                    <p><strong>Prix:</strong> {chambre.prix.toLocaleString()} FCFA/mois</p>
                                    <p><strong>Taille:</strong> {chambre.taille || 'Non spécifiée'}</p>
                                    <p><strong>Type:</strong> {chambre.type || 'Non spécifié'}</p>
                                    <p>
                                        <strong>Meublée:</strong>
                                        <Badge variant={chambre.meublee ? "default" : "outline"} className="ml-2">
                                            {chambre.meublee ? 'Oui' : 'Non'}
                                        </Badge>
                                    </p>
                                    <p>
                                        <strong>SDB Privée:</strong>
                                        <Badge variant={chambre.salle_de_bain ? "default" : "outline"} className="ml-2">
                                            {chambre.salle_de_bain ? 'Oui' : 'Non'}
                                        </Badge>
                                    </p>
                                </div>
                            </CardContent>
                            <CardFooter className="p-4 pt-0">
                                <Link to={`/locataire/chambres/${chambre.id}`} className="w-full">
                                    <Button className="w-full">Voir les détails</Button>
                                </Link>
                            </CardFooter>
                        </Card>
                    ))}
                </div>
            )}
        </div>
    );
};

export default LocataireSearchPage;