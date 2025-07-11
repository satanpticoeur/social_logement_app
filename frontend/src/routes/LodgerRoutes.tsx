import React, { Suspense } from 'react';
import { Route, Routes } from 'react-router-dom';

const LodgerSearchPage = React.lazy(() => import('@/pages/lodger/LodgerSearchPage.tsx'));
const LodgerChambreDetailsPage = React.lazy(() => import('@/pages/lodger/LodgerRoomDetailsPage.tsx'));
const LodgerContratsPage = React.lazy(() => import('@/pages/lodger/LodgerContractsPage.tsx'));
const LodgerPaiementsPage = React.lazy(() => import('@/pages/lodger/LodgerPaymentsPage.tsx'));

const LodgerRoutes: React.FC = () => {
    return (
        <Suspense fallback={<div>Chargement ...</div>}>
            <Routes>
                <Route path="" element={<LodgerSearchPage />} />
                <Route path="chambres/:chambreId" element={<LodgerChambreDetailsPage />} />
                <Route path="contrats" element={<LodgerContratsPage />} />
                <Route path="contrats/:contratId/paiements" element={<LodgerPaiementsPage />} />
            </Routes>
        </Suspense>
    );
};

export default LodgerRoutes;