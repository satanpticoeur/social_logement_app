
import React, { Suspense } from 'react';
import { Route, Routes } from 'react-router-dom';

import PrivateRoute from '@/components/PrivateRoute'
import PaymentDashboardPage from "@/pages/PaymentDashboardPage.tsx";
import ContractDetailPage from "@/pages/contract/ContractDetailPage.tsx";


// Pages Propriétaire
const OwnerDashboardPage = React.lazy(() => import('@/pages/owner/Dashboard'));
const OwnerClientsPage = React.lazy(() => import('@/pages/owner/OwnerClientsPage'));
const OwnerHousesPage = React.lazy(() => import('@/pages/owner/OwnerHousesPage'));
const OwnerRoomsPage = React.lazy(() => import('@/pages/owner/OwnerRoomsPage'));
const OwnerContractsPage = React.lazy(() => import('@/pages/owner/OwnerContractsPage'));
const ProprietairePaiementsPage = React.lazy(() => import('@/pages/ProprietairePaiementsPage'));
const DashboardLayoutPage = React.lazy(() => import('@/pages/owner/DashboardLayout'));

const OwnerRoutes: React.FC = () => {
    return (
        <Suspense fallback={<div>Chargement ...</div>}>
            <Routes>
                <Route path="/owner/dashboard" element={<PrivateRoute><DashboardLayoutPage /></PrivateRoute>}>
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