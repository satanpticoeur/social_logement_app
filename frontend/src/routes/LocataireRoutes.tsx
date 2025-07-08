import React, { Suspense } from 'react';
import { Route, Routes } from 'react-router-dom';

const LocataireSearchPage = React.lazy(() => import('@/pages/LocataireSearchPage'));
const LocataireChambreDetailsPage = React.lazy(() => import('@/pages/LocataireChambreDetailsPage'));
const LocataireContratsPage = React.lazy(() => import('@/pages/LocataireContratsPage'));
const LocatairePaiementsPage = React.lazy(() => import('@/pages/LocatairePaiementsPage'));

const LocataireRoutes: React.FC = () => {
    return (
        <Suspense fallback={<div>Chargement ...</div>}>
            <Routes>
                {/* Les chemins sont relatifs à "/locataire/" */}
                <Route path="recherche" element={<LocataireSearchPage />} />
                <Route path="chambres/:chambreId" element={<LocataireChambreDetailsPage />} />
                <Route path="contrats" element={<LocataireContratsPage />} />
                <Route path="contrats/:contratId/paiements" element={<LocatairePaiementsPage />} />
            </Routes>
        </Suspense>
    );
};

export default LocataireRoutes;