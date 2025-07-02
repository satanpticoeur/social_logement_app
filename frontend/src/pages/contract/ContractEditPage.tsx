// frontend/src/pages/ContractEditPage.tsx

import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import ContractForm from '../../components/forms/ContractForm.tsx';
import type {Contrat} from '../../types/common.ts';

const ContractEditPage: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const [contrat, setContrat] = useState<Contrat | null>(null);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

    useEffect(() => {
        if (!id) {
            setError("ID de contrat manquant pour la modification.");
            setLoading(false);
            return;
        }

        fetch(`${BACKEND_URL}/api/contrats/${id}`)
            .then(response => {
                if (!response.ok) {
                    if (response.status === 404) {
                        throw new Error("Contrat non trouvé pour modification.");
                    }
                    throw new Error(`Erreur HTTP: ${response.status}`);
                }
                return response.json();
            })
            .then((data: Contrat) => {
                setContrat(data);
                setLoading(false);
            })
            .catch((err: Error) => {
                console.error("Erreur lors de la récupération du contrat pour modification:", err);
                setError("Erreur lors du chargement du contrat pour modification: " + err.message);
                setLoading(false);
            });
    }, [id, BACKEND_URL]);

    if (loading) {
        return <div className="text-center mt-10 text-muted-foreground">Chargement du contrat pour modification...</div>;
    }

    if (error) {
        return <div className="text-destructive text-center mt-10">Erreur : {error}</div>;
    }

    if (!contrat) {
        return <div className="text-center mt-10 text-muted-foreground">Contrat non disponible pour modification.</div>;
    }

    return <ContractForm contratToEdit={contrat} />;
};

export default ContractEditPage;