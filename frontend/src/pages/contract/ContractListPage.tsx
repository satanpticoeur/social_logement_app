// frontend/src/pages/ContractListPage.tsx

import React, {useState, useEffect} from 'react';
import type {Contrat} from '../../types/common.ts';
// import {Card, CardContent, CardHeader, CardTitle} from '@/components/ui/card';
import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow} from '@/components/ui/table.tsx';
import {Badge} from '@/components/ui/badge.tsx'; // Si tu as besoin de badges pour les statuts ou types
import {Button} from '@/components/ui/button.tsx';
import {EditIcon, EyeIcon, PlusCircleIcon, TrashIcon} from "lucide-react";
import {Link} from "react-router-dom";

const ContractListPage: React.FC = () => {
    const [contrats, setContrats] = useState<Contrat[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

    useEffect(() => {
        fetch(`${BACKEND_URL}/api/contrats`, {
            method: 'GET',
            credentials: 'include',
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Erreur HTTP: ${response.status}`);
                }
                return response.json();
            })
            .then((data: Contrat[]) => {
                setContrats(data);
                setLoading(false);
            })
            .catch((err: Error) => {
                console.error("Erreur lors de la récupération des contrats:", err);
                setError("Erreur lors du chargement des contrats: " + err.message);
                setLoading(false);
            });
    }, [BACKEND_URL]);

    if (error) {
        return <div className="text-destructive text-center mt-10">Erreur : {error}</div>;
    }

    return (
        <div className="p-4 bg-background text-foreground  max-w-6xl mx-auto">
            <div className="flex justify-between items-center mb-8">
                <h1 className="text-3xl font-bold text-foreground">Liste des Contrats</h1>
                <Link to="/contracts/new/">
                    <Button>
                        <PlusCircleIcon className="mr-2 h-4 w-4"/>
                        Créer un nouveau contrat
                    </Button>
                </Link>
            </div>
            {loading ? (
                <p className="text-center text-muted-foreground">Chargement des contrats...</p>
            ) : contrats.length > 0 ? (
                <div className="bg-card rounded-lg shadow-md overflow-hidden border border-border">
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>#</TableHead>
                                <TableHead>Chambre</TableHead>
                                <TableHead>Locataire</TableHead>
                                <TableHead>Début</TableHead>
                                <TableHead>Fin</TableHead>
                                <TableHead>Caution</TableHead>
                                <TableHead>Statut</TableHead>
                                <TableHead className="text-right">Actions</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {contrats.map(contrat => (
                                <TableRow key={contrat.id} className="hover:bg-muted/50">
                                    <TableCell className="font-medium">{contrat.id}</TableCell>
                                    <TableCell>{contrat.chambre?.titre || 'N/A'}</TableCell>
                                    <TableCell>{contrat.locataire?.nom_utilisateur || 'N/A'}</TableCell>
                                    <TableCell>{new Date(contrat.date_debut).toLocaleDateString()}</TableCell>
                                    <TableCell>{new Date(contrat.date_fin).toLocaleDateString()}</TableCell>
                                    <TableCell>{contrat.montant_caution.toLocaleString()} XOF
                                        /{contrat.mois_caution} mois</TableCell>
                                    <TableCell>
                                        <Badge variant={
                                            contrat.statut === 'actif' ? 'default' : 'destructive'}>{contrat.statut}</Badge>
                                    </TableCell>
                                    <TableCell className="text-right">
                                        {/* Futures actions comme voir les détails, modifier, etc. */}
                                        <Link to={`/contracts/${contrat.id}`}>
                                            <Button variant={"outline"} size={"sm"}>
                                                <EyeIcon/>
                                            </Button>
                                        </Link>

                                        <Link to={`/contracts/${contrat.id}/edit`}>
                                            <Button variant={"outline"} className="ml-2" size={"sm"}>
                                                <EditIcon/>
                                            </Button>
                                        </Link>
                                        <Link to={`/contracts/${contrat.id}/delete`}>
                                            <Button variant={"outline"} className="ml-2 hover:text-destructive"
                                                    size={"sm"}>
                                                <TrashIcon/>
                                            </Button>
                                        </Link>


                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </div>
            ) : (
                <p className="text-center text-muted-foreground mt-8">Aucun contrat trouvé pour le moment.</p>
            )}
        </div>
    );
};

export default ContractListPage;