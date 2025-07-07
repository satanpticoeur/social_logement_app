import {BrowserRouter as Router, Routes, Route} from 'react-router-dom';
import {HomePage} from './pages/HomePage';
import {UserListPage} from './pages/user/UserListPage.tsx';
import {RoomListPage} from "@/pages/RoomListPage.tsx";
import PaymentDashboardPage from "@/pages/PaymentDashboardPage.tsx";
import ContractListPage from "@/pages/contract/ContractListPage.tsx";
import ContractDetailPage from "@/pages/contract/ContractDetailPage.tsx";
import ContractEditPage from "@/pages/contract/ContractEditPage.tsx";
import ContractCreatePage from "@/pages/contract/ContractCreatePage.tsx";
import {AuthProvider} from "@/context/AuthContext.tsx";
import LoginPage from "@/pages/auth/LoginPage.tsx";
import RegisterPage from "@/pages/auth/RegisterPage.tsx";
import PrivateRoute from "@/components/PrivateRoute.tsx";
import OwnerDashboardPage from "@/pages/owner/Dashboard.tsx";
import OwnerClientsPage from "@/pages/owner/OwnerClientsPage.tsx";
import OwnerHousesPage from "@/pages/owner/OwnerHousesPage.tsx";
import OwnerRoomsPage from "@/pages/owner/OwnerRoomsPage.tsx";
import OwnerContractsPage from "@/pages/owner/OwnerContractsPage.tsx";
import DashboardLayoutPage from "@/pages/owner/DashboardLayout.tsx";
import {LandingPage} from "@/pages/LandingPage.tsx";
import LocataireSearchPage from "@/pages/LocataireSearchPage.tsx";
import LocataireChambreDetailsPage from "@/pages/LocataireChambreDetailsPage.tsx";
import LocataireContratsPage from "@/pages/LocataireContratsPage.tsx";
import LocatairePaiementsPage from "@/pages/LocatairePaiementsPage.tsx";
import ProprietairePaiementsPage from "@/pages/ProprietairePaiementsPage.tsx";

function App() {
    return (
        <Router>
            <AuthProvider>
                <main className="container mx-auto p-4">
                    <Routes>
                        <Route path="/" element={<HomePage/>}>
                            <Route index element={<LandingPage/>}/>
                            <Route path="/login" element={<LoginPage/>}/>
                            <Route path="/register" element={<RegisterPage/>}/>
                            <Route path="/houses" element={<PrivateRoute><h1>Liste des maisons</h1></PrivateRoute>}/>
                            <Route path="/rooms" element={<PrivateRoute> <RoomListPage/> </PrivateRoute>}/>
                            <Route path="/payments" element={<PrivateRoute> <PaymentDashboardPage/> </PrivateRoute>}/>
                            <Route path="/contracts" element={<PrivateRoute> <ContractListPage/> </PrivateRoute>}/>
                            <Route path="/contracts/:id"
                                   element={<PrivateRoute> <ContractDetailPage/> </PrivateRoute>}/>
                            <Route path="/contracts/:id/edit"
                                   element={<PrivateRoute> <ContractEditPage/> </PrivateRoute>}/>
                            <Route path="/contracts/create"
                                   element={<PrivateRoute> <ContractCreatePage/> </PrivateRoute>}/>
                            <Route path="/users" element={<PrivateRoute> <UserListPage/> </PrivateRoute>}/>

                            <Route path="/locataire/recherche" element={<LocataireSearchPage />} />
                            <Route path="/locataire/chambres/:chambreId" element={<LocataireChambreDetailsPage />} />
                            <Route path="/locataire/contrats" element={<LocataireContratsPage />} />
                            {/* Route pour les détails d'un contrat locataire si besoin (non implémentée ici mais utile) */}
                            {/* <Route path="/locataire/contrats/:contratId" element={<LocataireContratDetailsPage />} /> */}
                            <Route path="/locataire/contrats/:contratId/paiements" element={<LocatairePaiementsPage />} /> {/* Nouvelle route */}
                        </Route>

                        {/*Routes du proprietaire*/}
                        <Route path="/owner/dashboard" element={<PrivateRoute><DashboardLayoutPage/></PrivateRoute>}>
                            <Route index element={<OwnerDashboardPage/>}/>
                            <Route path="/owner/dashboard/clients"
                                   element={<PrivateRoute> <OwnerClientsPage/></PrivateRoute>}/>
                            <Route path="/owner/dashboard/payments"
                                   element={<PrivateRoute> <PaymentDashboardPage/></PrivateRoute>}/>
                            <Route path="/owner/dashboard/houses"
                                   element={<PrivateRoute><OwnerHousesPage/></PrivateRoute>}/>
                            <Route path="/owner/dashboard/houses/:houseID/rooms"
                                   element={<PrivateRoute><OwnerRoomsPage/> </PrivateRoute>}/>
                            <Route path="/owner/dashboard/rooms"
                                   element={<PrivateRoute> <OwnerRoomsPage/></PrivateRoute>}/>
                            <Route path="/owner/dashboard/contracts"
                                   element={<PrivateRoute> <OwnerContractsPage/></PrivateRoute>}/>
                            <Route path="/owner/dashboard/contracts/:id"
                                   element={<PrivateRoute> <ContractDetailPage/></PrivateRoute>}/>
                            <Route path="/owner/dashboard/contracts/:id/payments"
                                   element={<PrivateRoute> <ProprietairePaiementsPage/></PrivateRoute>}/>
                            {/* Route pour les détails d'un contrat propriétaire si besoin (non implémentée ici mais utile) */}
                            {/* <Route path="/proprietaire/contrats/:contratId" element={<ProprietaireContratDetailsPage />} /> */}
                        </Route>

                        {/* Route 404 */}
                        <Route path="*"
                               element={<h1 className="text-center text-3xl mt-10"> 404 - Page non trouvée</h1>}/>
                    </Routes>
                </main>
            </AuthProvider>
        </Router>
    );
}

export default App;