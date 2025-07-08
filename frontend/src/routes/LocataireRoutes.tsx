import React, { Suspense } from 'react';
import { Route, Routes } from 'react-router-dom';

const LocataireSearchPage = React.lazy(() => import('@/pages/lodger/LodgerSearchPage.tsx'));
const LocataireChambreDetailsPage = React.lazy(() => import('@/pages/lodger/LodgerRoomDetailsPage.tsx'));
const LocataireContratsPage = React.lazy(() => import('@/pages/lodger/LodgerContractsPage.tsx'));
const LocatairePaiementsPage = React.lazy(() => import('@/pages/lodger/LodgerPaymentsPage.tsx'));

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