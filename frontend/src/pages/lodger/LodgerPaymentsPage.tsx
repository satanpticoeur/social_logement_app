import React, { useEffect, useState, useCallback } from 'react';
import { authenticatedFetch } from '@/lib/api.ts';
import { toast } from 'sonner';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table.tsx";
import { Badge } from "@/components/ui/badge.tsx";
import { format } from 'date-fns';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Loader2 } from 'lucide-react'; // Pour l'icône de chargement
import { useLocation, useNavigate } from 'react-router-dom'; // Importez ces hooks de React Router

// Interfaces (inchangées)
interface PaiementData {
    id: number;
    montant: number;
    date_echeance: string;
    date_paiement: string | null;
    statut: string; // 'impaye', 'paye', 'en_retard', 'en_cours_traitement'
    description: string;
}

interface ContratPaiements {
    contrat_id: number;
    chambre_titre: string;
    chambre_adresse: string;
    proprietaire_nom: string;
    statut_contrat: string;
    date_debut_contrat: string;
    date_fin_contrat: string;
    paiements: PaiementData[];
}

const LodgerPaymentsPage: React.FC = () => {
    const [mesPaiementsParContrat, setMesPaiementsParContrat] = useState<ContratPaiements[]>([]);
    const [loading, setLoading] = useState(true);

    // États pour le dialogue de paiement
    const [showPaymentDialog, setShowPaymentDialog] = useState(false);
    const [selectedPayment, setSelectedPayment] = useState<PaiementData | null>(null);
    const [phoneNumber, setPhoneNumber] = useState('771234567'); // Valeur par défaut
    const [operator, setOperator] = useState('Orange Money'); // Valeur par défaut
    const [isInitiatingPayment, setIsInitiatingPayment] = useState(false);

    // Hooks de React Router
    const location = useLocation();
    const navigate = useNavigate();

    // Utilisez useCallback pour mémoriser la fonction de récupération des paiements
    const fetchMesPaiements = useCallback(async () => {
        setLoading(true);
        try {
            const data: ContratPaiements[] = await authenticatedFetch('locataire/mes-paiements', { method: 'GET' });
            setMesPaiementsParContrat(data);
        } catch (error: any) {
            console.error('Erreur lors du chargement des paiements:', error);
            toast.error("Échec du chargement des paiements.", { description: error.message || "Erreur inconnue." });
        } finally {
            setLoading(false);
        }
    }, []); // Aucune dépendance car fetchMesPaiements ne dépend de rien qui change au fil du temps.

    useEffect(() => {
        // Appeler la fonction de chargement initiale
        fetchMesPaiements();

        // Gérer les paramètres d'URL après une redirection PayDunya
        const urlParams = new URLSearchParams(location.search);
        const token = urlParams.get('token');
        const status = urlParams.get('status');
        const message = urlParams.get('message');

        if (token && status) {
            console.log(`Token reçu: ${token}, Statut: ${status}, Message: ${message}`);
            switch (status) {
                case 'success':
                    toast.success("Paiement effectué avec succès !", {
                        description: `Votre transaction pour le token ${token} a été confirmée.`,
                        duration: 5000,
                    });
                    break;
                case 'completed': // Au cas où le backend renvoie "completed" directement
                    toast.success("Paiement effectué avec succès !", {
                        description: `Votre transaction pour le token ${token} a été confirmée.`,
                        duration: 5000,
                    });
                    break;
                case 'cancelled':
                    toast.warning("Paiement annulé.", {
                        description: `La transaction pour le token ${token} a été annulée.`,
                        duration: 5000,
                    });
                    break;
                case 'failed':
                    toast.error("Échec du paiement.", {
                        description: `La transaction pour le token ${token} a échoué. ${message || ''}`,
                        duration: 5000,
                    });
                    break;
                case 'pending': // Si le statut est "pending" après redirection (moins commun pour return_url)
                    toast.info("Paiement en attente de confirmation.", {
                        description: `La transaction pour le token ${token} est en attente.`,
                        duration: 5000,
                    });
                    break;
                case 'error':
                    toast.error("Une erreur est survenue lors du paiement.", {
                        description: message || "Veuillez réessayer ou contacter le support.",
                        duration: 5000,
                    });
                    break;
                default:
                    toast.info("Statut de paiement inconnu.", {
                        description: `Une réponse inattendue a été reçue pour le token ${token}.`,
                        duration: 5000,
                    });
            }
            fetchMesPaiements();

            navigate(location.pathname, { replace: true });
        }
    }, [location.search, navigate, fetchMesPaiements]); // fetchMesPaiements comme dépendance de useEffect

    const getPaiementStatusBadgeVariant = (status: string) => {
        switch (status) {
            case 'paye': return 'default'; // Ou 'success' si Badge supporte
            case 'impaye': return 'secondary';
            case 'en_retard': return 'destructive';
            case 'en_cours_traitement': return 'outline'; // Un badge plus neutre pour "en cours"
            default: return 'secondary';
        }
    };

    const handleOpenPaymentDialog = (payment: PaiementData) => {
        setSelectedPayment(payment);
        setShowPaymentDialog(true);
        // Les valeurs par défaut sont déjà dans le useState
    };

    const handleInitiatePayDunyaPayment = async () => {
        if (!selectedPayment || !phoneNumber || !operator) {
            toast.error("Veuillez remplir tous les champs nécessaires.");
            return;
        }

        setIsInitiatingPayment(true);
        try {
            const response = await authenticatedFetch(`locataire/paiements/${selectedPayment.id}/initier-paydunya`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ phone_number: phoneNumber, operator: operator }),
            });

            console.log("Réponse de l'initialisation du paiement PayDunya:", response);

            if (response.status === 'initiated' && response.redirect_url) {
                toast.info(response.message || "Redirection vers PayDunya...", { duration: 3000 });
                // Rediriger l'utilisateur vers la page de paiement PayDunya
                window.location.href = response.redirect_url;
                // Important: ne pas fermer le dialogue ici, la redirection prend le relais.
                // Le rechargement des paiements sera géré par l'useEffect après la redirection
                // si le paiement est complété/annulé.
            } else {
                toast.error(response.message || "Échec de l'initialisation du paiement PayDunya.", {
                    description: response.error_details || "Vérifiez vos informations ou réessayez.",
                });
                setShowPaymentDialog(false); // Fermer le dialogue en cas d'échec
            }
        } catch (error: any) {
            console.error('Erreur lors de l\'initialisation du paiement PayDunya:', error);
            toast.error("Échec de l'initialisation du paiement PayDunya.", { description: error.message || "Erreur inconnue." });
            setShowPaymentDialog(false); // Fermer le dialogue en cas d'erreur
        } finally {
            setIsInitiatingPayment(false);
        }
    };

    if (loading) {
        return <div className="text-center p-8">Chargement de vos paiements...</div>;
    }

    return (
        <div className="container mx-auto p-4">
            <h1 className="text-3xl font-bold mb-6 text-center">Mes Paiements de Location</h1>

            {mesPaiementsParContrat.length === 0 ? (
                <div className="text-center p-8 text-gray-600 border rounded-lg">
                    <p className="text-lg">Vous n'avez aucun paiement enregistré pour le moment.</p>
                </div>
            ) : (
                <div className="space-y-8">
                    {mesPaiementsParContrat.map((contrat) => (
                        <Card key={contrat.contrat_id}>
                            <CardHeader>
                                <CardTitle>Contrat pour {contrat.chambre_titre}</CardTitle>
                                <CardDescription>
                                    Avec {contrat.proprietaire_nom} ({contrat.chambre_adresse})
                                    <br/>
                                    Du {format(new Date(contrat.date_debut_contrat), 'dd/MM/yyyy')} au {format(new Date(contrat.date_fin_contrat), 'dd/MM/yyyy')}
                                    <Badge variant="outline" className="ml-2">Statut du contrat: {contrat.statut_contrat.replace('_', ' ')}</Badge>
                                </CardDescription>
                            </CardHeader>
                            <CardContent>
                                {contrat.paiements.length === 0 ? (
                                    <p className="text-gray-500 text-center">Aucun paiement enregistré pour ce contrat.</p>
                                ) : (
                                    <Table>
                                        <TableHeader>
                                            <TableRow>
                                                <TableHead>Description</TableHead>
                                                <TableHead>Montant</TableHead>
                                                <TableHead>Échéance</TableHead>
                                                <TableHead>Date Paiement</TableHead>
                                                <TableHead>Statut</TableHead>
                                                <TableHead className="text-right">Action</TableHead>
                                            </TableRow>
                                        </TableHeader>
                                        <TableBody>
                                            {contrat.paiements.map((paiement) => (
                                                <TableRow key={paiement.id}>
                                                    <TableCell>{paiement.description}</TableCell>
                                                    <TableCell>{paiement.montant.toLocaleString()} FCFA</TableCell>
                                                    <TableCell>{format(new Date(paiement.date_echeance), 'dd/MM/yyyy')}</TableCell>
                                                    <TableCell>{paiement.date_paiement ? format(new Date(paiement.date_paiement), 'dd/MM/yyyy') : 'N/A'}</TableCell>
                                                    <TableCell>
                                                        <Badge variant={getPaiementStatusBadgeVariant(paiement.statut)} className={`
                                                            ${paiement.statut === 'impaye' ? 'bg-yellow-100 text-yellow-800' : ''}
                                                            ${paiement.statut === 'en_retard' ? 'bg-red-100 text-red-800' : ''}
                                                            ${paiement.statut === 'en_cours_traitement' ? 'bg-blue-100 text-blue-800' : ''}
                                                            ${paiement.statut === 'paye' ? 'bg-green-100 text-green-800' : ''}
                                                        `}>
                                                            {paiement.statut.replace(/_/g, ' ')}
                                                        </Badge>
                                                    </TableCell>
                                                    <TableCell className="text-right">
                                                        {(paiement.statut === 'impaye' || paiement.statut === 'en_retard') ? (
                                                            <Button
                                                                variant="default"
                                                                size="sm"
                                                                onClick={() => handleOpenPaymentDialog(paiement)}
                                                                disabled={isInitiatingPayment}
                                                            >
                                                                Payer avec Mobile Money
                                                            </Button>
                                                        ) : (
                                                            <span className="text-gray-500 text-sm">
                                                                {paiement.statut === 'en_cours_traitement' ? (
                                                                    <span className="flex items-center">
                                                                        <Loader2 className="mr-2 h-4 w-4 animate-spin" /> En attente...
                                                                    </span>
                                                                ) : 'Payé'}
                                                            </span>
                                                        )}
                                                    </TableCell>
                                                </TableRow>
                                            ))}
                                        </TableBody>
                                    </Table>
                                )}
                            </CardContent>
                        </Card>
                    ))}
                </div>
            )}

            {/* Dialogue de paiement Mobile Money */}
            <Dialog open={showPaymentDialog} onOpenChange={setShowPaymentDialog}>
                <DialogContent className="sm:max-w-[425px]">
                    <DialogHeader>
                        <DialogTitle>Payer l'échéance de {selectedPayment?.montant.toLocaleString()} FCFA</DialogTitle>
                        <DialogDescription>
                            Veuillez entrer votre numéro de téléphone Mobile Money et choisir votre opérateur.
                        </DialogDescription>
                    </DialogHeader>
                    <div className="grid gap-4 py-4">
                        <div className="grid grid-cols-4 items-center gap-4">
                            <Label htmlFor="phoneNumber" className="text-right">
                                Numéro
                            </Label>
                            <Input
                                id="phoneNumber"
                                type="tel"
                                value={phoneNumber}
                                onChange={(e) => setPhoneNumber(e.target.value)}
                                className="col-span-3"
                                placeholder="Ex: 771234567"
                            />
                        </div>
                        <div className="grid grid-cols-4 items-center gap-4">
                            <Label htmlFor="operator" className="text-right">
                                Opérateur
                            </Label>
                            <Select onValueChange={setOperator} value={operator}>
                                <SelectTrigger className="col-span-3">
                                    <SelectValue placeholder="Choisir un opérateur" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="Orange Money">Orange Money</SelectItem>
                                    <SelectItem value="Wave">Wave</SelectItem>
                                    <SelectItem value="Free Money">Free Money</SelectItem>
                                    {/* Assurez-vous que ces valeurs correspondent à celles que PayDunya attend ou que vous mappez côté backend */}
                                </SelectContent>
                            </Select>
                        </div>
                    </div>
                    <DialogFooter>
                        <Button
                            onClick={handleInitiatePayDunyaPayment}
                            disabled={isInitiatingPayment || !phoneNumber || !operator}
                        >
                            {isInitiatingPayment ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Initialisation...
                                </>
                            ) : (
                                'Confirmer le paiement'
                            )}
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    );
};

export default LodgerPaymentsPage;