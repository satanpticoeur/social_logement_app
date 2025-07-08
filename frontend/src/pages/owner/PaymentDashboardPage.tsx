import React, {useEffect, useMemo, useState} from 'react';
import type {Paiement} from '../../types/common.ts';
import {Card, CardContent, CardHeader, CardTitle} from '@/components/ui/card.tsx';
import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow} from '@/components/ui/table.tsx';

const PaymentDashboardPage: React.FC = () => {
    const [paiements, setPaiements] = useState<Paiement[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

    useEffect(() => {
        fetch(`${BACKEND_URL}/api/paiements`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Erreur HTTP: ${response.status}`);
                }
                return response.json();
            })
            .then((data: Paiement[]) => {
                setPaiements(data);
                setLoading(false);
            })
            .catch((err: Error) => {
                console.error("Erreur lors de la récupération des paiements:", err);
                setError("Erreur lors du chargement des paiements: " + err.message);
                setLoading(false);
            });
    }, [BACKEND_URL]);

    // Calcul des totaux et agrégations
    const {totalPaid, totalUnpaid, countPaid, countUnpaid} = useMemo(() => {
        let paid = 0;
        let unpaid = 0;
        let cPaid = 0;
        let cUnpaid = 0;

        paiements.forEach(p => {
            if (p.statut === 'payé') {
                paid += p.montant;
                cPaid++;
            } else if (p.statut === 'impayé') {
                unpaid += p.montant;
                cUnpaid++;
            }
            // Ignorer 'partiel' pour l'instant ou le gérer différemment
        });

        return {totalPaid: paid, totalUnpaid: unpaid, countPaid: cPaid, countUnpaid: cUnpaid};
    }, [paiements]);

    if (error) {
        return <div className="text-destructive text-center mt-10">Erreur : {error}</div>;
    }

    return (
        <div className="p-4 bg-background text-foreground">
            <h1 className="text-3xl font-bold mb-8 text-center text-foreground">Dashboard des Paiements</h1>

            {loading ? (
                <p className="text-center text-muted-foreground">Chargement des données de paiements...</p>
            ) : (
                <>
                    {/* Cartes de Résumé */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8 max-w-4xl mx-auto">
                        <Card className="shadow-lg">
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                <CardTitle className="text-sm font-medium">Paiements Réglés</CardTitle>
                                <svg
                                    xmlns="http://www.w3.org/2000/svg"
                                    viewBox="0 0 24 24"
                                    fill="none"
                                    stroke="currentColor"
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth="2"
                                    className="h-4 w-4 text-muted-foreground"
                                >
                                    <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
                                </svg>
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold">{totalPaid.toLocaleString()} XOF</div>
                                <p className="text-xs text-muted-foreground">
                                    {countPaid} paiements
                                </p>
                            </CardContent>
                        </Card>

                        <Card className="shadow-lg">
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                <CardTitle className="text-sm font-medium">Paiements Impayés</CardTitle>
                                <svg
                                    xmlns="http://www.w3.org/2000/svg"
                                    viewBox="0 0 24 24"
                                    fill="none"
                                    stroke="currentColor"
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth="2"
                                    className="h-4 w-4 text-muted-foreground"
                                >
                                    <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/>
                                    <circle cx="9" cy="7" r="4"/>
                                    <path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>
                                </svg>
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold">{totalUnpaid.toLocaleString()} XOF</div>
                                <p className="text-xs text-muted-foreground">
                                    {countUnpaid} paiements
                                </p>
                            </CardContent>
                        </Card>
                    </div>

                    {/* Liste des Paiements */}
                    <h2 className="text-2xl font-bold mb-4 text-foreground text-center">Détails des Paiements</h2>
                    {paiements.length > 0 ? (
                        <div
                            className="bg-card rounded-lg shadow-md overflow-hidden border border-border max-w-6xl mx-auto">
                            <Table>
                                <TableHeader>
                                    <TableRow>
                                        <TableHead>Contrat ID</TableHead>
                                        <TableHead>Chambre</TableHead>
                                        <TableHead>Locataire</TableHead>
                                        <TableHead>Montant</TableHead>
                                        <TableHead>Date de Paiement</TableHead>
                                        <TableHead>Statut</TableHead>
                                    </TableRow>
                                </TableHeader>
                                <TableBody>
                                    {paiements.map(paiement => (
                                        <TableRow key={paiement.id} className="hover:bg-muted/50">
                                            <TableCell className="font-medium">{paiement.contrat_id}</TableCell>
                                            <TableCell>{paiement.contrat?.chambre?.titre || 'N/A'}</TableCell>
                                            <TableCell>{paiement.contrat?.locataire?.nom_utilisateur || 'N/A'}</TableCell>
                                            <TableCell>{paiement.montant.toLocaleString()} XOF</TableCell>
                                            <TableCell>{new Date(paiement.date_paiement).toLocaleDateString()}</TableCell>
                                            <TableCell>
                        <span
                            className={`inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset ${
                                paiement.statut === 'payé'
                                    ? 'bg-green-50 text-green-700 ring-green-600/20 dark:bg-green-900 dark:text-green-200 dark:ring-green-700/30'
                                    : paiement.statut === 'impayé'
                                        ? 'bg-red-50 text-red-700 ring-red-600/20 dark:bg-red-900 dark:text-red-200 dark:ring-red-700/30'
                                        : 'bg-yellow-50 text-yellow-700 ring-yellow-600/20 dark:bg-yellow-900 dark:text-yellow-200 dark:ring-yellow-700/30'
                            }`}>
                          {paiement.statut}
                        </span>
                                            </TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        </div>
                    ) : (
                        <p className="text-center text-muted-foreground mt-8">Aucun paiement trouvé.</p>
                    )}
                </>
            )}
        </div>
    );
};

export default PaymentDashboardPage;