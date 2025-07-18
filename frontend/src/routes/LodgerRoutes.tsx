import React, {Suspense} from 'react';
import {Route, Routes} from 'react-router-dom';

const LodgerSearchPage = React.lazy(() => import('@/pages/lodger/LodgerSearchPage.tsx'));
const LodgerChambreDetailsPage = React.lazy(() => import('@/pages/lodger/LodgerRoomDetailsPage.tsx'));
const LodgerContratsPage = React.lazy(() => import('@/pages/lodger/LodgerMyContractsPage.tsx'));
const LodgerPaiementsPage = React.lazy(() => import('@/pages/lodger/LodgerPaymentsPage.tsx'));
const LodgerDashboardLayoutPage = React.lazy(() => import('@/pages/lodger/LodgerDashboardLayout.tsx'));
const LodgerDashboardPage = React.lazy(() => import('@/pages/lodger/LodgerDashboardPage.tsx'));
const LodgerMyRequestsPage = React.lazy(() => import('@/pages/lodger/LodgerPendingRequestsPage.tsx'));
const LodgerMyRoomsPage = React.lazy(() => import('@/pages/lodger/LodgerMyRoomsPage.tsx'));

const LodgerRoutes: React.FC = () => {
    return (
        <Suspense fallback={<div>Chargement ...</div>}>
            <Routes>
                <Route index element={<LodgerSearchPage/>}/>
                <Route path="dashboard" element={<LodgerDashboardLayoutPage/>}>
                    <Route index element={<LodgerDashboardPage/>}/>
                    <Route path="rooms" element={<LodgerMyRoomsPage/>}/>
                    <Route path="rooms/:roomId" element={<LodgerChambreDetailsPage/>}/>
                    <Route path="contrats" element={<LodgerContratsPage/>}/>
                    <Route path="contrats/:contratId/paiements" element={<LodgerPaiementsPage/>}/>
                    <Route path="mes-demandes" element={<LodgerMyRequestsPage/>}/>
                    <Route path="paiements" element={<LodgerPaiementsPage/>}/>
                </Route>
            </Routes>
        </Suspense>
    );
};

export default LodgerRoutes;