import React, {Suspense} from 'react';
import {Route, Routes} from 'react-router-dom';
import {HomePage} from '@/pages/HomePage';
import {LandingPage} from "@/pages/LandingPage.tsx";
import SearchRoomDetailsPage from "@/components/room/SearchRoomDetailsDialog.tsx";

const LodgerRoutes = React.lazy(() => import('./LodgerRoutes.tsx'));
const OwnerRoutes = React.lazy(() => import('./OwnerRoutes.tsx'));
const LoginPage = React.lazy(() => import('@/pages/auth/LoginPage'));
const RegisterPage = React.lazy(() => import('@/pages/auth/RegisterPage'));
const RoomListPage = React.lazy(() => import('@/pages/RoomListPage'));


export const AppRoutes: React.FC = () => {
    return (
        <Suspense fallback={<div>Chargement de la page...</div>}>
            <Routes>
                <Route path="/" element={<HomePage/>}>
                    <Route index element={<LandingPage/>}/>
                    <Route path="login" element={<LoginPage/>}/>
                    <Route path="register" element={<RegisterPage/>}/>
                    <Route path="rooms" element={<RoomListPage/>}/>
                    <Route path="rooms/:roomId" element={<SearchRoomDetailsPage />}/>
                </Route>
                <Route path="lodger/*" element={<LodgerRoutes/>}/>

                <Route path="owner/dashboard/*" element={<OwnerRoutes/>}/>

                <Route path="*" element={<h1 className="text-center text-3xl mt-10"> 404 - Page non trouvée</h1>}/>
            </Routes>
        </Suspense>
    );
};