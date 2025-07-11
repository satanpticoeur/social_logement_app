
import React, { Suspense } from 'react';
import { Route, Routes } from 'react-router-dom';

import PrivateRoute from '@/components/PrivateRoute'


// Pages Propriétaire
const OwnerDashboardPage = React.lazy(() => import('@/pages/owner/OwnerDashboard.tsx'));
const OwnerClientsPage = React.lazy(() => import('@/pages/owner/OwnerClientsPage'));
const OwnerHousesPage = React.lazy(() => import('@/pages/owner/OwnerHousesPage'));
const OwnerRoomsPage = React.lazy(() => import('@/pages/owner/OwnerRoomsPage'));
const OwnerContractsPage = React.lazy(() => import('@/pages/owner/OwnerContractsPage'));
const ProprietairePaiementsPage = React.lazy(() => import('@/pages/owner/ProprietairePaiementsPage.tsx'));
const DashboardLayoutPage = React.lazy(() => import('@/pages/owner/OwnerDashboardLayout.tsx'));

const PaymentDashboardPage = React.lazy(() => import('@/pages/owner/PaymentDashboardPage.tsx'));
const ContractDetailPage = React.lazy(() => import('@/pages/contract/ContractDetailPage'));

const OwnerRoutes: React.FC = () => {
    return (
        <Suspense fallback={<div>Chargement ...</div>}>
            <Routes>
                <Route path="/" element={<PrivateRoute><DashboardLayoutPage /></PrivateRoute>}>
                    <Route index element={<OwnerDashboardPage />} />
                    <Route path="clients" element={<PrivateRoute> <OwnerClientsPage /></PrivateRoute>} />
                    <Route path="payments" element={<PrivateRoute> <PaymentDashboardPage /></PrivateRoute>} />
                    <Route path="houses" element={<PrivateRoute><OwnerHousesPage /></PrivateRoute>} />
                    <Route path="houses/:houseID/rooms" element={<PrivateRoute><OwnerRoomsPage /> </PrivateRoute>} />
                    <Route path="rooms" element={<PrivateRoute> <OwnerRoomsPage /></PrivateRoute>} />
                    <Route path="contracts" element={<PrivateRoute> <OwnerContractsPage /></PrivateRoute>} />
                    <Route path="contracts/:id" element={<PrivateRoute> <ContractDetailPage /></PrivateRoute>} />
                    <Route path="contracts/:id/payments" element={<PrivateRoute> <ProprietairePaiementsPage /></PrivateRoute>} />
                </Route>

                {/* Route 404 */}
                <Route path="*" element={<h1 className="text-center text-3xl mt-10"> 404 - Page non trouvée</h1>} />
            </Routes>
        </Suspense>
    );
};

export default OwnerRoutes;